import env
from sqlalchemy import and_
from db_queries import db_session, get_event_matchings, get_service_matchings_by_keys, get_trust_reports, get_gps_reports
from models import Trust, GPS, ServiceMatching, EventMatching
from utils import date_to_iso, iso_to_date, get_service_key, get_matching_key

def from_service_matching_pkey(pkey):
    service_matching = db_session.query(ServiceMatching).get(pkey)
    db_session.close()
    if service_matching is not None:
        return from_service_matching(service_matching)

def from_service_matching(service_matching):

    matching = service_matching.as_dict()

    service = get_service_key(matching)
    gps_car_id = matching['gps_car_id']

    trust_reports = get_trust_reports(service, start=matching['start'], end=matching['end'])
    gps_reports = get_gps_reports(gps_car_id, start=matching['start'], end=matching['end'])

    return get_segment_blueprint(
        headcode=matching['headcode'],
        origin_location=matching['origin_location'],
        origin_departure=matching['origin_departure'],
        gps_car_id=gps_car_id,
        trust=trust_reports,
        gps=gps_reports,
        start=matching['start'],
        end=matching['end'],
        total_matching=matching['total_matching'],
        total_missed_in_between=matching['total_missed_in_between'],
        median_time_error=matching['median_time_error'],
        iqr_time_error=matching['iqr_time_error'])

def from_matchings_diff(service, unit_matchings_diff):
    all_segments = []

    # first segment is the service alone
    service_segment = get_service_segment(service)
    all_segments.append(service_segment)

    # rest are with paired with units
    for diff_type, units in unit_matchings_diff.iteritems():

        # service matchings that exist on the database can be retrieved from there
        pkeys = set(service + (unit,) for unit in units)
        service_matchings = get_service_matchings_by_keys(pkeys)
        segments = map(from_service_matching, list(service_matchings))
        for segment in segments:
            segment['type'] = diff_type

        # service matchings that don't exist on the database will be created with
        # all trust & gps reports between the time interval the service was running
        found_pkeys = set(get_matching_key(s.as_dict()) for s in service_matchings)
        not_found_pkeys = pkeys - found_pkeys
        for pkey in not_found_pkeys:
            headcode, origin_location, origin_departure, gps_car_id = pkey
            segment = get_segment_blueprint(headcode=headcode,
                                            origin_location=origin_location,
                                            origin_departure=origin_departure,
                                            gps_car_id=gps_car_id,
                                            type=diff_type)
            if not diff_type == 'no_data':
                service = pkey[0:3]
                trust_reports = get_trust_reports(service, end=env.now)
                event_times = map(lambda s: s.event_time, trust_reports)
                start = min(event_times)
                end = max(event_times)
                gps_reports = get_gps_reports(gps_car_id, start, end)
                segment['trust'] = trust_reports
                segment['gps'] = gps_reports
                segment['start'] = start
                segment['end'] = end
            segments.append(segment)

        all_segments += segments
    return all_segments

def from_matchings_diff_serialized(service, unit_matchings_diff):
    return map(serialize_segment, from_matchings_diff(service, unit_matchings_diff))

def get_service_segment(service):
    headcode, origin_location, origin_departure = service
    trust_reports = get_trust_reports(service, end=env.now)
    return get_segment_blueprint(
        headcode=headcode,
        origin_location=origin_location,
        origin_departure=origin_departure,
        trust=trust_reports,
        type='service')

def get_segment_blueprint(**props):
    segment = {
      'headcode': None,
      'origin_location': None,
      'origin_departure': None,
      'gps_car_id': None,
      'trust': [],
      'gps': [],
      'start': None,
      'end': None,
      'type': None
    }
    segment.update(props)
    return segment

def transform_fields(a_dict, fields, transform):
    for field in fields:
        if field in a_dict and a_dict[field] is not None:
            a_dict[field] = transform(a_dict[field])
    return a_dict

def serialize_segment(segment):
    transform_fields(segment, ['origin_departure', 'start', 'end'], date_to_iso)
    transform_fields(segment, ['trust', 'gps'], lambda x: map(serialize_report, x))
    return segment

def serialize_report(report):
    report = report.as_dict()
    transform_fields(report, ['origin_departure', 'event_time'], date_to_iso)
    return report

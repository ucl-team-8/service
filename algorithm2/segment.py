from sqlalchemy import and_
from db_queries import db_session, get_event_matchings, get_service_matchings_by_keys
from models import Trust, GPS, ServiceMatching, EventMatching
from utils import date_to_iso, get_service_key

def from_service_matching_pkey(pkey):
    service_matching = db_session.query(ServiceMatching).get(pkey)
    if service_matching is not None:
        return from_service_matching(service_matching)

def from_service_matching(service_matching):

    segment = service_matching.as_dict()

    service = get_service_key(segment)
    gps_car_id = segment['gps_car_id']

    trust_reports = db_session.query(Trust).filter_by(
        headcode=segment['headcode'],
        origin_location=segment['origin_location'],
        origin_departure=segment['origin_departure']
    ).filter(and_(
        Trust.event_time >= segment['start'],
        Trust.event_time <= segment['end'])
    )

    gps_reports = db_session.query(GPS).filter_by(
        gps_car_id=gps_car_id
    ).filter(and_(
        GPS.event_time >= segment['start'],
        GPS.event_time <= segment['end'])
    )

    matchings = get_event_matchings(service, gps_car_id)

    segment['origin_departure'] = date_to_iso(segment['origin_departure'])
    segment['start'] = date_to_iso(segment['start'])
    segment['end'] = date_to_iso(segment['end'])
    segment['trust'] = map(serialize_report, trust_reports)
    segment['gps'] = map(serialize_report, gps_reports)
    segment['matching_ids'] = matching_ids = [(m.trust_id, m.gps_id) for m in matchings]

    return segment

def serialize_report(report):
    report = report.as_dict()
    report['event_time'] = date_to_iso(report['event_time'])
    if 'origin_departure' in report:
        report['origin_departure'] = date_to_iso(report['origin_departure'])
    return report

def from_matchings_diff(service, unit_matchings_diff):
    all_segments = []

    # first segment is the service alone
    all_segments.append(get_service_segment(service))

    # rest are with paired with units
    for diff_type, units in unit_matchings_diff.iteritems():
        pkeys = [service + (unit,) for unit in units]
        service_matchings = get_service_matchings_by_keys(pkeys)
        # TODO: if there are no service matchings, generate with start to end
        segments = map(from_service_matching, list(service_matchings))
        for segment in segments:
            segment['type'] = diff_type
        all_segments += segments
    return all_segments

def get_service_segment(service):

    segment = dict()

    headcode, origin_location, origin_departure = service

    trust_reports = db_session.query(Trust).filter_by(
        headcode=service[0],
        origin_location=service[1],
        origin_departure=service[2]
    )

    return {
        'headcode': headcode,
        'origin_location': origin_location,
        'origin_departure': date_to_iso(origin_departure),
        'trust': map(serialize_report, trust_reports),
        'gps': [],
        'type': 'service',
        'matching_ids': []
    }

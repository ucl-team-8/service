from sqlalchemy import and_
from db_queries import db_session, get_event_matchings
from models import Trust, GPS, ServiceMatching, EventMatching

def from_service_matching_pkey(pkey):
    service_matching = db_session.query(ServiceMatching).get(pkey)
    if service_matching is not None:
        return from_service_matching(service_matching)

def from_service_matching(service_matching):

    headcode = service_matching.headcode,
    origin_location = service_matching.origin_location,
    origin_departure = service_matching.origin_departure
    gps_car_id = service_matching.gps_car_id
    start = service_matching.start
    end = service_matching.end

    trust_reports = db_session.query(Trust).filter_by(
        headcode=headcode,
        origin_location=origin_location,
        origin_departure=origin_departure
    ).filter(and_(
        Trust.event_time >= start,
        Trust.event_time <= end)
    )

    gps_reports = db_session.query(GPS).filter_by(
        gps_car_id=gps_car_id
    ).filter(and_(
        GPS.event_time >= start,
        GPS.event_time <= end)
    )

    service = (headcode, origin_location, origin_departure)
    matchings = get_event_matchings(service, gps_car_id)

    matching_ids = [(m.trust_id, m.gps_id) for m in matchings]

    return {
        'headcode': headcode,
        'origin_location': origin_location,
        'origin_departure': origin_departure,
        'gps_car_id': gps_car_id,
        'trust': [r.as_dict() for r in trust_reports],
        'gps': [r.as_dict() for r in gps_reports],
        'matching_ids': matching_ids
    }

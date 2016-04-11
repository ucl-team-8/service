from app_db import db
from models import EventMatching, ServiceMatching

def get_event_matchings(service, unit):
    headcode, origin_location, origin_departure = service
    gps_car_id = unit
    return db.session.query(EventMatching).filter_by(
        headcode=headcode,
        origin_location=origin_location,
        origin_departure=origin_departure,
        gps_car_id=gps_car_id)

def get_service_matching(service, unit):
    primary_key = service + (unit,)
    return db.session.query(ServiceMatching).get(primary_key)

# def get_service_maching_existing_keys(pkeys):
#     db.session.query(
#         ServiceMatching.headcode,
#         Ser)

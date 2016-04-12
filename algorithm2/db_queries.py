from app_db import app
from models import EventMatching, ServiceMatching

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db_session = scoped_session(sessionmaker(bind=engine,
                                         autoflush=True,
                                         autocommit=False))

def get_event_matchings(service, unit):
    headcode, origin_location, origin_departure = service
    gps_car_id = unit
    return db_session.query(EventMatching).filter_by(
        headcode=headcode,
        origin_location=origin_location,
        origin_departure=origin_departure,
        gps_car_id=gps_car_id).all()

def get_service_matching(service, unit):
    primary_key = service + (unit,)
    return db_session.query(ServiceMatching).get(primary_key)

def get_service_matchings_for_unit(unit):
    return db_session.query(ServiceMatching).filter_by(gps_car_id=unit)

# TODO: finish this
# def get_service_maching_existing_keys(pkeys):
#     db_session.query(
#         ServiceMatching.headcode,
#         ServiceMatching.origin_location,
#         ServiceMatching.origin_departure
#     ).filter()

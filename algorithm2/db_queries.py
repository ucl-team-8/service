from app_db import app
import sqlalchemy.sql
from sqlalchemy.sql import and_, or_
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

def get_service_matchings_by_keys(pkeys):
    if not pkeys: return db_session.query(ServiceMatching).filter(sqlalchemy.sql.false())
    pkey_predicates = map(construct_pkey_predicate, pkeys)
    return db_session.query(
        ServiceMatching.headcode,
        ServiceMatching.origin_location,
        ServiceMatching.origin_departure,
        ServiceMatching.gps_car_id
    ).filter(
        or_(*pkey_predicates)
    )

def construct_pkey_predicate(pkey):
    return and_(ServiceMatching.headcode==pkey[0],
                ServiceMatching.origin_location==pkey[1],
                ServiceMatching.origin_departure==pkey[2],
                ServiceMatching.gps_car_id==pkey[3])

from algorithm2 import env
from algorithm2.utils import serialize_matchings, get_service_key, date_to_iso
from algorithm2.db_queries import get_service_matchings_by_keys
from algorithm2 import segment
from app_db import db, socketio, dispatcher
from flask import request, jsonify
from flask_socketio import send, emit
from models import Trust, GPS, GeographicalLocation

@socketio.on('connect')
def onconnect():
    emit('locations', get_locations())
    dispatcher.subscribe('time', request.sid)
    dispatcher.subscribe('matchings', request.sid)
    dispatcher.dispatch('time', date_to_iso(env.now))
    dispatcher.dispatch('matchings', serialize_matchings(get_matchings()))
    print("Client connected")

@socketio.on('subscribe')
def subscribe(service_dict):
    service = get_service_key(service_dict)
    matchings = get_matchings()

    segments = []

    if service in matchings:
        unit_matchings_diff = matchings[service]
        segments = segment.from_matchings_diff_serialized(service, unit_matchings_diff)

    dispatcher.subscribe(service, request.sid)
    dispatcher.dispatch_service(service, segments)

@socketio.on('unsubscribe')
def unsubscribe(service_dict):
    service = get_service_key(service_dict)
    dispatcher.unsubscribe(service, request.sid)

@socketio.on('disconnect')
def ondisconnect():
    print("Client disconnected")
    dispatcher.unsubscribe_from_all(request.sid)

def get_matchings():
    env.matchings_lock.acquire()
    matchings = env.matchings
    env.matchings_lock.release()
    return matchings

def get_locations():

    trust_tiplocs = db.session.query(Trust.tiploc).all()
    gps_tiplocs = db.session.query(GPS.tiploc).all()

    tiplocs = set()
    tiplocs.update([x[0] for x in trust_tiplocs])
    tiplocs.update([x[0] for x in gps_tiplocs])

    records = db.session.query(GeographicalLocation).filter(
        GeographicalLocation.tiploc.in_(tiplocs)
    ).all()

    db.session.close()

    return [r.as_dict() for r in records]

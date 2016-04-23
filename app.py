from flask import render_template, jsonify
from sqlalchemy.sql import func, and_
from app_db import app, db, socketio, dispatcher
from collections import defaultdict
from algorithm2.segment import serialize_segment
import app_socketio
import sys
import os

from models import *

def extract_dict(record):
    return record.as_dict()

@app.route("/visualisation")
def hello():
    return render_template('visualisation.html')

@app.route("/basic-algorithm")
def basic_algorithm():
    return render_template("basic-algorithm.html")


@app.route("/")
def trainMap():
    return render_template("live.html")


@app.route("/events/trust.json")
def trust():
    records = db.session.query(Trust, Schedule).\
              outerjoin(Schedule, and_(Trust.headcode==Schedule.headcode,
                                       Trust.origin_departure==Schedule.origin_departure,
                                       Trust.origin_location==Schedule.origin_location))
    def extract_dict(record):
        trust, schedule = record
        result = trust.as_dict()
        if schedule:
            result['gps_car_id'] = schedule.unit
        return result

    return jsonify(result=map(extract_dict, records))


@app.route("/events/gps.json")
def gps():
    records = db.session.query(GPS)
    return jsonify(result=map(extract_dict, records))

@app.route("/data/allocations.json")
def allocations():
    records = db.session.query(Schedule)
    return jsonify(result=map(extract_dict, records))

@app.route("/data/services.json")
def services():
    records = db.session.query(Trust)
    reports = map(extract_dict, records)
    services = defaultdict(list)
    for r in reports:
        key = (r['headcode'], r['origin_location'], r['origin_departure'])
        value = {key: r[key] for key in r if key in ['id', 'event_time', 'event_type', 'tiploc']}
        services[key].append(value)
    result = list()
    for key, reports in services.iteritems():
        result.append({
            'headcode': key[0],
            'origin_location': key[1],
            'origin_departure': key[2],
            'reports': reports
        })
    return jsonify(result=map(serialize_segment, result))

@app.route("/data/units.json")
def units():
    records = db.session.query(GPS)
    reports = map(extract_dict, records)
    units = defaultdict(list)
    for r in reports:
        key = r['gps_car_id']
        value = {key: r[key] for key in r if key in ['id', 'event_time', 'event_type', 'tiploc']}
        units[key].append(value)
    result = list()
    for key, reports in units.iteritems():
        result.append({
            'gps_car_id': key,
            'reports': reports
        })
    return jsonify(result=map(serialize_segment, result))

@app.route("/data/augmented_matchings.json")
def augmented_matchings():
    return jsonify(result=app_socketio.get_augmented_matchings())

@app.route("/data/locations.json")
def locations():
    return jsonify(result=app_socketio.get_locations())


if __name__ == "__main__":
    # when the server is restarting, the environment variable is set to 'true'
    # this is to avoid running the algorithm again after a restart
    # if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    from algorithm2.simulator import Simulator
    simulator = Simulator(dispatcher=dispatcher)
    simulator.deamon = True
    simulator.start()
    # app.run(use_reloader=False)
    socketio.run(app, use_reloader=False, debug=True)

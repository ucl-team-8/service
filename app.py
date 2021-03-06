from flask import render_template, jsonify
from sqlalchemy.sql import func, and_
from app_db import app, db, socketio, dispatcher
import app_socketio
import sys
import os

from models import *

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

    def extract_dict(record):
        result = record.as_dict()
        return result

    return jsonify(result=map(extract_dict, records))


@app.route("/data/schedule.json")
def schedule():
    records = db.session.query(Schedule, UnitToGPSMapping).\
              outerjoin(UnitToGPSMapping, Schedule.unit==UnitToGPSMapping.unit)

    def extract_dict(record):
        schedule, mapping = record
        result = schedule.as_dict()
        if mapping:
            result['gps_car_id'] = mapping.gps_car_id
        return result

    return jsonify(result=map(extract_dict, records))


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

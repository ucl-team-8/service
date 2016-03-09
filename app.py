from flask import render_template, jsonify
from sqlalchemy.sql import func, and_
import os
import sys
from app_db import app, db

app.config.from_object(os.environ['APP_SETTINGS'])

from models import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/algorithm')
import simrealtime
import globals

@app.route("/")
def hello():
    return render_template('visualisation.html')


@app.route("/basic-algorithm")
def basic_algorithm():
    return render_template("basic-algorithm.html")


@app.route("/layerTwo")
def layerTwo():
    return render_template("layerTwo.html")


@app.route("/events/trust.json")
def trust():
    records = db.session.query(Trust, Schedule, UnitToGPSMapping).\
              outerjoin(Schedule, and_(Trust.headcode==Schedule.headcode,
                                       Trust.origin_departure==Schedule.origin_departure)).\
              outerjoin(UnitToGPSMapping, Schedule.unit==UnitToGPSMapping.unit)

    def extract_dict(record):
        trust, schedule, mapping = record
        result = trust.as_dict()
        if mapping:
            result['gps_car_id'] = mapping.gps_car_id
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


@app.route("/events/gps.json")
def gps():
    records = db.session.query(GPS).filter(func.length(GPS.gps_car_id) == 5)

    def extract_dict(record):
        result = record.as_dict()
        return result

    return jsonify(result=map(extract_dict, records))

@app.route("/data/segments.json")
def segments():
    globals.lock.acquire()
    results = map(lambda x: x.__dict__, globals.segments)
    globals.lock.release()
    results = jsonify({'results': results})
    return results

if __name__ == "__main__":
    temp = simrealtime.SimulateRealTime(globals.speedup)
    temp.start()
    app.run()
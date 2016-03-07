from flask import Flask, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, and_
from copy import deepcopy
import simrealtime
import globals
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)
from models import *


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


@app.route("/segments")
def segments():
    globals.lock.acquire()
    results = deepcopy(globals.segments)
    results = map(lambda x: x.__dict__, results)
    for result in results:
        for match in result['matching']:
            if match['time_error'] is not None:
                match['time_error'] = match['time_error'].total_seconds() * 100
    results = jsonify({'results': results})
    globals.lock.release()
    return results

if __name__ == "__main__":
    temp = simrealtime.SimulateRealTime(globals.speedup)
    temp.start()
    app.run()

from flask import render_template, jsonify
from sqlalchemy.sql import func, and_
from app_db import app, db, socketio
import sys
import os

from models import *
from algorithm2.simulator import Simulator
from algorithm2.consumer import Consumer
from algorithm2.matcher import Matcher

@app.route("/")
def hello():
    return render_template('visualisation.html')


@app.route("/basic-algorithm")
def basic_algorithm():
    return render_template("basic-algorithm.html")


@app.route("/map")
def trainMap():
    return render_template("map.html")


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


@socketio.on('connection')
def handle_message(message):
    print("Client connected")


matcher = Matcher()
consumer = Consumer(matcher=matcher)
simulator = Simulator(consumer=consumer)

if __name__ == "__main__":

    # app.run()

    simulator.clear_tables()
    simulator.simulate()
    matcher.run()

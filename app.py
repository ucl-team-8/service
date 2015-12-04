from flask import Flask, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import *

@app.route("/")
def hello():
    return render_template('visualisation.html')

@app.route("/basic-algorithm")
def basic_algorithm():
    return render_template("basic-algorithm.html")

def convert_to_dicts(records):
    return [record.as_dict() for record in records]

@app.route("/events/trust.json")
def trust():
    records = db.session.query(Trust, Schedule, UnitToGPSMapping).\
              filter(Trust.headcode==Schedule.headcode).\
              filter(Trust.origin_departure==Schedule.origin_departure).\
              filter(Schedule.unit==UnitToGPSMapping.unit)

    def extract_dict(record):
        trust, schedule, mapping = record
        result = trust.as_dict()
        result['gps_car_id'] = mapping.gps_car_id
        return result

    return jsonify(result=map(extract_dict, records))

@app.route("/events/gps.json")
def gps():
    records = db.session.query(GPS).filter(func.length(GPS.gps_car_id) == 5)
    return jsonify(result=convert_to_dicts(records))

if __name__ == "__main__":
    app.run()

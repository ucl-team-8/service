from flask import Flask, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import *

@app.route("/")
def hello():
    return render_template('visualisation.html')

def convert_to_dicts(records):
    return [record.as_dict() for record in records]

@app.route("/events/trust.json")
def trust():
    records = db.session.query(Trust, Schedule, UnitToGPSMapping).\
              filter(Trust.CIF_uid==Schedule.CIF_uid).\
              filter(Schedule.unit==UnitToGPSMapping.unit)

    def extract_dict(record):
        trust, schedule, mapping = record
        result = trust.as_dict()
        result['gps_car_id'] = mapping.gps_car_id
        return result

    return jsonify(result=map(extract_dict, records))

@app.route("/events/gps.json")
def gps():
    records = db.session.query(GPS).all()
    return jsonify(result=convert_to_dicts(records))

if __name__ == "__main__":
    app.run()

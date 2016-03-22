from flask import render_template, jsonify
from sqlalchemy.sql import func, and_
from app_db import app, db, socketio
import sys
import os


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


@app.route("/map")
def trainMap():
    return render_template("map.html")


@app.route("/layerTwo")
def layerTwo():
    return render_template("layerTwo.html")


@app.route("/events/trust.json")
def trust():
    globals.db_lock.acquire()
    records = db.session.query(Trust, Schedule, UnitToGPSMapping).\
              outerjoin(Schedule, and_(Trust.headcode==Schedule.headcode,
                                       Trust.origin_departure==Schedule.origin_departure)).\
              outerjoin(UnitToGPSMapping, Schedule.unit==UnitToGPSMapping.unit)
    globals.db_lock.release()
    def extract_dict(record):
        trust, schedule, mapping = record
        result = trust.as_dict()
        if mapping:
            result['gps_car_id'] = mapping.gps_car_id
        return result

    return jsonify(result=map(extract_dict, records))


@app.route("/events/gps.json")
def gps():
    globals.db_lock.acquire()
    records = db.session.query(GPS).filter(func.length(GPS.gps_car_id) == 5)
    globals.db_lock.release()

    def extract_dict(record):
        result = record.as_dict()
        return result

    return jsonify(result=map(extract_dict, records))


@app.route("/data/schedule.json")
def schedule():
    globals.db_lock.acquire()
    records = db.session.query(Schedule, UnitToGPSMapping).\
              outerjoin(UnitToGPSMapping, Schedule.unit==UnitToGPSMapping.unit)
    globals.db_lock.release()

    def extract_dict(record):
        schedule, mapping = record
        result = schedule.as_dict()
        if mapping:
            result['gps_car_id'] = mapping.gps_car_id
        return result

    return jsonify(result=map(extract_dict, records))


@app.route("/data/gps.json")
def gpsData():
    globals.db_lock.acquire()
    records = None
    if len(simulation.records['gps']) > 0:
        records = db.session.query(GPS).filter(and_(func.length(GPS.gps_car_id) == 5, GPS.event_time <= simulation.records['gps'][0]['event_time']))
    else:
        records = db.session.query(GPS).filter(func.length(GPS.gps_car_id) == 5)
    globals.db_lock.release()

    def extract_dict(record):
        result = record.as_dict()
        return result

    result = map(extract_dict, records)
    result.sort(key=lambda x: x['event_time'])
    return jsonify(result=result)


@app.route("/data/trust.json")
def trustData():
    globals.db_lock.acquire()
    records = None
    if len(simulation.records['trust']) > 0:
        records = db.session.query(Trust).filter(Trust.event_time <= simulation.records['trust'][0]['event_time'])
    else:
        records = db.session.query(Trust)
    globals.db_lock.release()

    def extract_dict(record):
        result = record.as_dict()
        return result

    result = map(extract_dict, records)
    result.sort(key=lambda x: x['event_time'])
    return jsonify(result=result)


# Because datetime.time is not JSON serializable
# we stringify it
def stringifyTime(record):
    if record['arrive_time'] is not None:
        record['arrive_time'] = str(record['arrive_time'])
    if record['depart_time'] is not None:
        record['depart_time'] = str(record['depart_time'])
    if record['pass_time'] is not None:
        record['pass_time'] = str(record['pass_time'])
    return record


@app.route("/data/diagram/<headcode>")
def diagramData(headcode):
    globals.db_lock.acquire()
    result = db.session.query(DiagramService).filter(
        DiagramService.headcode == headcode
    )
    result = map(lambda x: x.as_dict(), result)
    if len(result) > 0:
        diagram_service = result[0]
    else:
        globals.db_lock.release()
        return jsonify(result=None)

    result = db.session.query(DiagramStop).filter(
        DiagramStop.diagram_service_id == diagram_service['id']
    )
    globals.db_lock.release()

    diagram_service['stop'] = map(lambda x: stringifyTime(x.as_dict()), result)

    return jsonify(result=diagram_service)


# Returns a merge value of 2 dicts
def mergeTwoDicts(a, b):
    c = a.copy()
    c.update(b)
    return c


@app.route("/data/segments.json")
def segments():
    globals.lock.acquire()
    results = mergeTwoDicts(globals.segments, globals.old_segments)
    results = map(lambda x: x.__dict__, results.values())
    globals.lock.release()
    results = jsonify({'results': results})
    return results


@app.route("/data/old_segments.json")
def oldSegments():
    globals.lock.acquire()
    results = map(lambda x: x.__dict__, globals.old_segments.values())
    globals.lock.release()
    results = jsonify({'results': results})
    return results


@socketio.on('connection')
def handle_message(message):
    print("Client connected")


simulation = None

if __name__ == "__main__":
    simulation = simrealtime.SimulateRealTime(globals.speedup)
    simulation.start()
    app.run()

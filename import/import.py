from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET
import datetime
import csv
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from models import *

# TODO: Can we please change csv header names?
# TODO: Check the columns in schedule where len(unit) == 5 and where cif_uid is empty
# TODO: Use bulk inserts

def open_file(filename):
    try:
        f = open(filename, 'rb')
        return f
    except IOError:
        return None

def set_date(time_string, separator):
    if time_string == '':
        return None

    date = datetime.datetime.strptime(time_string, '%H'+separator+'%M'+separator+'%S')
    today = datetime.date.today()
    return date.replace(day = today.day, month = today.month, year = today.year)

def store_schedule(file):
    try:
        reader = csv.DictReader(file)
        for row in reader:
            if len(row['Unit']) > 4: #Some columns contain weird unit values and no cif_uid
                continue

            date = set_date(row['origin_dep_dt'], ':')
            schedule = Schedule(row['Unit'], row['headcode'], row['origin_loc'], date, row['cif_uid'])
            db.session.add(schedule)
            db.session.commit()
    except KeyError:
        print "csv file is not in correct format"

def store_trust(file):
    try:
        reader = csv.DictReader(file)
        for row in reader:
            arrival_report = set_date(row['Act Arrival Report'], '.')
            departure_report = set_date(row['Act Dep Report'], '.')
            origin_depart_time = set_date(row['Origin depart time'], '.')

            trust = Trust(row['Headcode'], row['Event location'], int(row['Loc Seq']), arrival_report,
            departure_report, bool(row['Is a planned stop?']), origin_depart_time, row['CIF Uid'], row['Category'])

            db.session.add(trust)
            db.session.commit()
    except KeyError:
        print "csv file is not in correct format"

def store_unit_to_gps(file):
    try:
        reader = csv.DictReader(file)
        for row in reader:
            unit_to_gps = UnitToGPSMapping(row['Unit'], row['GPS car id'])

            db.session.add(unit_to_gps)
            db.session.commit()
    except KeyError:
        print "csv file is not in correct format"

def translate_columns(gps_column_translation, x):
    """
    It 'translates' column names given a <original column> => <new column>
    dictionary, and a dictionary to be translated.
    """
    d = dict()
    for column_from, column_to in gps_column_translation.items():
        if column_from in x:
            d[column_to] = x[column_from]
    return d

gps_column_translation = {
    'device': 'gps_car_id',
    'eventType': 'event_type',
    'eventTime': 'event_time',
    'tiploc': 'tiploc'
}

def store_gps(file):
    root = ET.parse(file).getroot()
    gps_events = [gps_event.attrib for gps_event in root]
    rows = [translate_columns(gps_column_translation, gps_event) for gps_event in gps_events]
    for row in rows:
        row['event_time'] = datetime.datetime.strptime(row['event_time'], "%Y-%m-%dT%H:%M:%S")
        gps = GPS(**row)
        db.session.add(gps)
        db.session.commit()

def import_file(filename, table_name):
    f = open_file(filename)
    if f == None:
        print "File does not exist"
        return

    if table_name == "schedule":
        store_schedule(f)
    elif table_name == "trust":
        store_trust(f)
    elif table_name == "unit_to_gps":
        store_unit_to_gps(f)
    elif table_name == "gps":
        store_gps(f)
    else:
        print "Not a valid table name"

    f.close()


import_file('schedule.csv', 'schedule')
import_file('unit_to_gps.csv', 'unit_to_gps')
import_file('trust.csv', 'trust')
import_file('gpsData.xml', 'gps')

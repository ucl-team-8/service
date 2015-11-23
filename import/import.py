from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET
import datetime
import sys
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
        f = open(os.path.dirname(os.path.realpath(__file__)) + '/' + filename, 'rb')
        return f
    except IOError:
        return None

def file_length(file):
    for i, l in enumerate(file):
            pass
    return i + 1

def calculate_lengths(files):
    open_files(files)
    lengths = {'total_length': 0.0}
    for key, file in files.items():
        lengths[key] = file_length(file)
        lengths['total_length'] += lengths[key]

    lengths['finished'] = 0.0
    close_files(files)
    return lengths

def update_progress(lengths):
    lengths['finished'] += 1
    progress = int((lengths['finished']/lengths['total_length'])*100)
    percentage = (progress/5)
    sys.stdout.write('\r[{0}{1}] {2}%'.format('#'*percentage, ' '*(20 - percentage),progress))
    sys.stdout.flush()

def set_date(time_string, separator):
    if time_string == '':
        return None

    date = datetime.datetime.strptime(time_string, '%H'+separator+'%M'+separator+'%S')
    today = datetime.date.today()
    return date.replace(day = today.day, month = today.month, year = today.year)

def delete_data():
    db.session.query(Trust).delete()
    db.session.query(Schedule).delete()
    db.session.query(GPS).delete()
    db.session.query(UnitToGPSMapping).delete()

def store_schedule(file, lengths):
    try:
        reader = csv.DictReader(file)
        for row in reader:
            update_progress(lengths)
            if len(row['Unit']) > 4: #Some columns contain weird unit values and no cif_uid
                continue

            date = set_date(row['origin_dep_dt'], ':')
            schedule = Schedule(row['Unit'], row['headcode'], row['origin_loc'], date, row['cif_uid'])
            db.session.add(schedule)
            db.session.commit()
    except KeyError:
        print "csv file is not in correct format"

def store_trust(file, lengths):
    try:
        reader = csv.DictReader(file)
        for row in reader:
            update_progress(lengths)
            arrival_report = set_date(row['Act Arrival Report'], '.')
            departure_report = set_date(row['Act Dep Report'], '.')
            origin_depart_time = set_date(row['Origin depart time'], '.')

            trust = Trust(row['Headcode'], row['Event location'], int(row['Loc Seq']), arrival_report,
            departure_report, bool(row['Is a planned stop?']), origin_depart_time, row['CIF Uid'], row['Category'])

            db.session.add(trust)
            db.session.commit()
    except KeyError:
        print "csv file is not in correct format"

def store_unit_to_gps(file, lengths):
    try:
        reader = csv.DictReader(file)
        for row in reader:
            update_progress(lengths)
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

def store_gps(file, lengths):
    root = ET.parse(file).getroot()
    gps_events = [gps_event.attrib for gps_event in root]
    rows = [translate_columns(gps_column_translation, gps_event) for gps_event in gps_events]
    for row in rows:
        update_progress(lengths)
        row['event_time'] = datetime.datetime.strptime(row['event_time'], "%Y-%m-%dT%H:%M:%S")
        gps = GPS(**row)
        db.session.add(gps)
        db.session.commit()

def open_files(files):
    files['schedule'] = open_file('schedule.csv')
    files['unit_to_gps'] = open_file('unit_to_gps.csv')
    files['trust'] = open_file('trust.csv')
    files['gpsData'] = open_file('gpsData.xml')

def close_files(files):
    for key, file in files.items():
        file.close()



def main():
    files = dict()
    lengths = calculate_lengths(files)
    open_files(files)
    delete_data()
    store_schedule(files['schedule'], lengths)
    store_unit_to_gps(files['unit_to_gps'], lengths)
    store_trust(files['trust'], lengths)
    store_gps(files['gpsData'], lengths)

    close_files(files)
    lengths['finished'] = lengths['total_length']
    update_progress(lengths)
    sys.stdout.write("\nSuccessfully added all files to db\n")

main()

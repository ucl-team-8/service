from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET
import datetime
import sys
import csv
import os

from latlon_converter import ENtoLL84

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from models import *

# TODO: Can we please change csv header names?
# TODO: Check the columns in schedule where len(unit) == 5 and where cif_uid is empty
# TODO: Use bulk inserts


def convert_to(datatype, value, *args, **kwargs):
    try:
        return datatype(value, *args, **kwargs)
    except:
        return None

# File handling

def open_file(filename):
    try:
        f = open(os.path.dirname(os.path.realpath(__file__)) + '/' + filename, 'rb')
        return f
    except IOError:
        return None


# Progress bar

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


# Date handling

def set_date(time_string, separator):
    if time_string == '':
        return None

    date = datetime.datetime.strptime(time_string, '%H'+separator+'%M'+separator+'%S')
    today = datetime.date.today()
    return date.replace(day=17, month=3, year=2015)


# Extracting data from files

def map_columns(column_map, x):
    """
    It 'translates' column names given a <original column> => <new column>
    dictionary, and a dictionary to be translated.
    """
    d = dict()
    for column_from, column_to in column_map.items():
        if column_from in x:
            d[column_to] = x[column_from]
    return d

trust_column_map = {
    'headcode': 'headcode',
    'origLoc': 'origin_location',
    'origDep': 'origin_departure',
    'tiploc': 'tiploc',
    'seq': 'seq',
    'eventType': 'event_type',
    'eventTime': 'event_time',
    'plannedPass': 'planned_pass'
}

gps_column_map = {
    'device': 'gps_car_id',
    'eventType': 'event_type',
    'eventTime': 'event_time',
    'tiploc': 'tiploc'
}

locations_column_map = {
    'Tiploc': 'tiploc',
    'Stanox': 'stanox',
    'CRS': 'crs',
    'Description': 'description',
    'P2X': 'easting',
    'P2Y': 'northing',
    'Type': 'type',
    'IsCIFStop': 'is_cif_stop',
    'CIFStopCount': 'cif_stop_count',
    'CIFPassCount': 'cif_pass_count'
}

def parse_xml(file):
    root = ET.parse(file).getroot()
    return [event.attrib for event in root]

def parse_trust(file):
    events = parse_xml(file)
    rows = [map_columns(trust_column_map, event) for event in events]
    for row in rows:
        row['origin_departure'] = datetime.datetime.strptime(row['origin_departure'], "%Y-%m-%dT%H:%M:%S")
        row['event_time'] = datetime.datetime.strptime(row['event_time'], "%Y-%m-%dT%H:%M:%S")
        row['planned_pass'] = convert_to(bool, row['planned_pass'])
        row['seq'] = convert_to(int, row['seq'])
    return rows

def parse_gps(file):
    events = parse_xml(file)
    rows = [map_columns(gps_column_map, event) for event in events]
    for row in rows:
        row['event_time'] = datetime.datetime.strptime(row['event_time'], "%Y-%m-%dT%H:%M:%S")
    return rows

def parse_locations(file):
    items = csv.DictReader(file, delimiter="\t")
    rows = [map_columns(locations_column_map, item) for item in items]
    for row in rows:

        if row['stanox'] == "0":
            # stanox 0 is not a valid stanox
            row['stanox'] = None

        row['is_cif_stop'] = convert_to(bool, row['is_cif_stop'])

        row['cif_stop_count'] = convert_to(int, row['cif_stop_count'])
        if row['cif_stop_count'] == 0: row['cif_stop_count'] = None

        row['cif_pass_count'] = convert_to(int, row['cif_pass_count'])
        if row['cif_pass_count'] == 0: row['cif_pass_count'] = None

        row['easting'] = convert_to(int, row['easting'])
        row['northing'] = convert_to(int, row['northing'])

        (e, n) = (row['easting'], row['northing'])

        if e and n and e != 0 and n != 0:
            (longitude, latitude) = ENtoLL84(row['easting'], row['northing'])
            row['longitude'] = longitude
            row['latitude'] = latitude

    return rows


# Storing data in database

def store_trust(file, lengths):
    rows = parse_trust(file)
    for row in rows:
        update_progress(lengths)
        trust = Trust(**row)
        db.session.add(trust)
        db.session.commit()

def store_gps(file, lengths):
    rows = parse_gps(file)
    for row in rows:
        update_progress(lengths)
        gps = GPS(**row)
        db.session.add(gps)
        db.session.commit()

def store_locations(file, lengths):
    rows = parse_locations(file)
    for row in rows:
        update_progress(lengths)
        location = GeographicalLocation(**row)
        db.session.add(location)
        db.session.commit()

def store_schedule(file, lengths):
    try:
        reader = csv.DictReader(file)
        for row in reader:
            update_progress(lengths)
            if len(row['Unit']) > 4: #Some columns contain weird unit values and no cif_uid
                continue

            date = set_date(row['origin_dep_dt'], ':')

            schedule = Schedule(
                unit=row['Unit'],
                headcode=row['headcode'],
                origin_location=row['origin_loc'],
                origin_departure=date,
                cif_uid=row['cif_uid'])

            db.session.add(schedule)
            db.session.commit()
    except KeyError:
        print "csv file is not in correct format"

def store_unit_to_gps(file, lengths):
    try:
        reader = csv.DictReader(file)
        for row in reader:
            update_progress(lengths)

            unit_to_gps = UnitToGPSMapping(
                unit=row['Unit'],
                gps_car_id=row['GPS car id'])

            db.session.add(unit_to_gps)
            db.session.commit()
    except KeyError:
        print "csv file is not in correct format"

def delete_data():
    db.session.query(Trust).delete()
    db.session.query(Schedule).delete()
    db.session.query(GPS).delete()
    db.session.query(UnitToGPSMapping).delete()
    db.session.query(GeographicalLocation).delete()


def open_files(files):
    files['schedule'] = open_file('../data/schedule.csv')
    files['unit_to_gps'] = open_file('../data/unit_to_gps.csv')
    files['trust'] = open_file('../data/trustData.xml')
    files['gpsData'] = open_file('../data/gpsData.xml')
    files['locations'] = open_file('../data/locations.tsv')

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
    store_locations(files['locations'], lengths)

    close_files(files)
    lengths['finished'] = lengths['total_length']
    update_progress(lengths)
    sys.stdout.write("\nSuccessfully added all files to db\n")

main()

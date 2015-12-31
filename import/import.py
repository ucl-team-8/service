from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET
import datetime
import math
import sys
import csv
import os

from latlon_converter import ENtoLL84

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from models import *

# TODO: Check the columns in schedule where len(unit) == 5 and where cif_uid is empty

def convert_to(datatype, value, *args, **kwargs):
    try:
        return datatype(value, *args, **kwargs)
    except:
        return None

# File handling

def open_file(filename):
    f = open(os.path.dirname(os.path.realpath(__file__)) + '/' + filename, 'rb')
    return f


# Date handling

def parse_date(date_string, date_format, time_only=False):
    if date_string == '':
        return None

    date = datetime.datetime.strptime(date_string, date_format)

    if time_only:
        return date.replace(day=17, month=3, year=2015)
    else:
        return date


# Extracting data from files

def parse_xml(file):
    root = ET.parse(file).getroot()
    return [event.attrib for event in root]

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

# TRUST

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

def parse_trust(file):
    events = parse_xml(file)
    rows = [map_columns(trust_column_map, event) for event in events]
    for row in rows:
        row['origin_departure'] = parse_date(row['origin_departure'], "%Y-%m-%dT%H:%M:%S")
        row['event_time'] = parse_date(row['event_time'], "%Y-%m-%dT%H:%M:%S")
        row['planned_pass'] = convert_to(bool, row['planned_pass'])
        row['seq'] = convert_to(int, row['seq'])
    return rows

# GPS

gps_column_map = {
    'device': 'gps_car_id',
    'eventType': 'event_type',
    'eventTime': 'event_time',
    'tiploc': 'tiploc'
}

def parse_gps(file):
    events = parse_xml(file)
    rows = [map_columns(gps_column_map, event) for event in events]
    for row in rows:
        row['event_time'] = parse_date(row['event_time'], "%Y-%m-%dT%H:%M:%S")
    return rows

# Schedule

schedule_column_map = {
    'Unit': 'unit',
    'headcode': 'headcode',
    'origin_loc': 'origin_location',
    'origin_dep_dt': 'origin_departure',
    'cif_uid': 'cif_uid'
}

def parse_schedule(file):
    reader = csv.DictReader(file)
    rows = [map_columns(schedule_column_map, row) for row in reader]
    rows = filter(lambda row: len(row['unit']) <= 4, rows)
    for row in rows:
        row['origin_departure'] = parse_date(row['origin_departure'], '%H:%M:%S', time_only=True)
    return rows

# Unit to GPS

unit_to_gps_column_map = {
    'Unit': 'unit',
    'GPS car id': 'gps_car_id'
}

def parse_unit_to_gps(file):
    reader = csv.DictReader(file)
    rows = [map_columns(unit_to_gps_column_map, row) for row in reader]
    return rows

# Locations

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

def store_rows(rows, model):
    db.session.bulk_insert_mappings(model, rows)

def delete_data():
    for model in [Trust, Schedule, GPS, UnitToGPSMapping, GeographicalLocation]:
        db.session.query(model).delete()

def open_files():
    return {
        'schedule': open_file('../data/schedule.csv'),
        'unit_to_gps': open_file('../data/unit_to_gps.csv'),
        'trust': open_file('../data/trustData.xml'),
        'gpsData': open_file('../data/gpsData.xml'),
        'locations': open_file('../data/locations.tsv')
    }

def close_files(files):
    for key, file in files.items():
        file.close()


def main():
    print("\nDeleting all existing data...\n")
    delete_data()

    files = open_files()

    print("Importing TRUST data...")
    store_rows(parse_trust(files['trust']), Trust)

    print("Importing GPS data...")
    store_rows(parse_gps(files['gpsData']), GPS)

    print("Importing Schedule data...")
    store_rows(parse_schedule(files['schedule']), Schedule)

    print("Importing Unit to GPS data...")
    store_rows(parse_unit_to_gps(files['unit_to_gps']), UnitToGPSMapping)

    print("Importing Locations data...")
    store_rows(parse_locations(files['locations']), GeographicalLocation)

    close_files(files)
    print("\nSuccessfully imported all data.\n")

if __name__ == "__main__":
    main()

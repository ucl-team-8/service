from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET
import argparse
import datetime
import math
import sys
import glob
import csv
import os

from latlon_converter import ENtoLL84

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)
from models import *
from app_db import db


# Parsing arguments for which dataset to import

parser = argparse.ArgumentParser(description='Import dataset.')
parser.add_argument('folder', type=str, help='Folder containing data.')

args = parser.parse_args()

# Conversion

def convert_to(datatype, value, *args, **kwargs):
    try:
        return datatype(value, *args, **kwargs)
    except:
        return None


# Date handling

def parse_date(date_string, date_format, time_only=False):
    if date_string == '' or date_string == '    ':
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
        row['planned_pass'] = row['planned_pass'] == 'true'
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

allocations_column_map = {
    'Unit': 'unit',
    'headcode': 'headcode',
    'origin_loc': 'origin_location',
    'origin_dep_dt': 'origin_departure',
    'cif_uid': 'cif_uid'
}


def parse_allocations(file):
    reader = csv.DictReader(file)
    rows = [map_columns(allocations_column_map, row) for row in reader]
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

        if row['stanox'] == "0" or row['stanox'] == "":
            # stanox 0 is not a valid stanox
            row['stanox'] = None

        if row['crs'] == "":
            row['crs'] = None

        row['is_cif_stop'] = convert_to(bool, row['is_cif_stop'])

        row['cif_stop_count'] = convert_to(int, row['cif_stop_count'])
        row['cif_pass_count'] = convert_to(int, row['cif_pass_count'])

        row['easting'] = convert_to(int, row['easting'])
        row['northing'] = convert_to(int, row['northing'])

        (e, n) = (row['easting'], row['northing'])

        if e and n and e != 0 and n != 0:
            (longitude, latitude) = ENtoLL84(row['easting'], row['northing'])
            row['longitude'] = longitude
            row['latitude'] = latitude
        else:
            row['easting'] = None
            row['northing'] = None

    return rows


# Checking if we have no empty strings in the values
def checkEmptyValues(dict):
    for key, value in dict.iteritems():
        if(type(value) is str and value.strip() == ''):
            dict[key] = None


# Parses the first line of a diagram txt file
def parseDiagramHeader(header):
    service = {'cif_uid': header[3:9]}
    service['date_runs_from'] = parse_date(header[9:15], '%y%m%d')
    service['date_runs_to'] = parse_date(header[15:21], '%y%m%d')
    service['days_run'] = header[21:28]
    service['train_category'] = header[30:32]
    service['headcode'] = header[32:36]
    service['train_class'] = header[66:67]

    checkEmptyValues(service)
    return service


# Parses all of the other lines in every diagram
# and records all of the stops
def parseDiagramStops(f, service):
    f.readline()  # skip additional information in the header
    stops = []
    for line in f:
        stop = {'diagram_service': service, 'diagram_service_id': service.id}
        stop['station_type'] = line[0:2]
        stop['tiploc'] = line[2:10]
        if(stop['station_type'] == 'LO'):
            stop['depart_time'] = parse_date(line[10:14], '%H%M')
            stop['engineering_allowance'] = convert_to(int, line[25:27].strip())
            stop['pathing_allowance'] = convert_to(int, line[27:29].strip())
        elif(stop['station_type'] == 'LI'):
            stop['arrive_time'] = parse_date(line[10:14], '%H%M')
            stop['depart_time'] = parse_date(line[15:19], '%H%M')
            stop['pass_time'] = parse_date(line[20:24], '%H%M')
            stop['engineering_allowance'] = convert_to(int, line[54:56].strip())
            stop['pathing_allowance'] = convert_to(int, line[56:58].strip())
        elif(stop['station_type'] == 'LT'):
            stop['arrive_time'] = parse_date(line[10:14], '%H%M')

        checkEmptyValues(stop)
        stops.append(stop)
    return stops


# loops over all of the files in the diagrams
# directory and extracts the data from them
def parseDiagrams():
    stops = []
    for filename in glob.glob(os.path.join(parentdir + '/data/diagrams', '*.txt')):
        f = open(filename, 'r')
        service = parseDiagramHeader(f.readline())
        service = DiagramService(**service)
        db.session.add(service)
        # We do not use bulk inserts atm because we want to get the id
        db.session.commit()
        db.session.flush()
        db.session.refresh(service)  # Making sure we have the id

        stops.extend(parseDiagramStops(f, service))
        f.close()
    return stops

# Storing data in database


def store_rows(rows, model):
    db.session.bulk_insert_mappings(model, rows)
    db.session.commit()


def delete_data():
    for model in [Trust, Schedule, GPS, UnitToGPSMapping, GeographicalLocation, DiagramStop, DiagramService]:
        db.session.query(model).delete()
    db.session.commit()

# File handling

def open_file(filename):
    path = os.path.join('data', filename)
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    f = open(os.path.join(project_path, path), 'rb')
    return f

def open_extract_file(filename):
    path = os.path.join(args.folder, filename)
    return open_file(path)

def open_files():
    return {
        'allocations': open_extract_file('allocations.csv'),
        'unit_to_gps': open_extract_file('unit_to_gps.csv'),
        'trust': open_extract_file('trustData.xml'),
        'gpsData': open_extract_file('gpsData.xml'),
        'locations': open_file('locations.tsv')
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

    print("Importing Allocations data...")
    store_rows(parse_allocations(files['allocations']), Schedule)

    print("Importing Unit to GPS data...")
    store_rows(parse_unit_to_gps(files['unit_to_gps']), UnitToGPSMapping)

    print("Importing Locations data...")
    store_rows(parse_locations(files['locations']), GeographicalLocation)

    close_files(files)

    print("Importing Diagram data...")
    stops = parseDiagrams()

    print("Importing Diagram Stops data...")
    store_rows(stops, DiagramStop)

    print("\nSuccessfully imported all data.\n")

if __name__ == "__main__":
    main()

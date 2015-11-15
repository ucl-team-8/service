from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import datetime
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from models import *

#TO DO: If the csv is not valid, do not store the values in db
#TO DO: Fix date (which is currently 1900)
#TO DO: Check the columns in schedule where len(unit) == 5 and where cif_uid is empty

def open_file(filename):
    try:
        f = open(filename, 'rb')
        return f
    except IOError:
        return None

def store_schedule(file):
    file.readline()  #Skip the first line with headings
    for row in file:
        values = row.split(',')
        if len(values[0]) > 4: #Some columns contain weird unit values and no cif_uid
            return
        date = datetime.datetime.strptime(values[3], "%H:%M:%S")
        schedule = Schedule(values[0], values[1], values[2], date, values[4].rstrip('\r\n'))
        db.session.add(schedule)
        db.session.commit()

def store_trust(file):
    file.readline()
    for row in file:
        values = row.split(',')
        if values[3] != "":
            values[3] = datetime.datetime.strptime(values[3], "%H.%M.%S")
        else:
            values[3] = None
        if values[4] != "":
            values[4]= datetime.datetime.strptime(values[4], "%H.%M.%S")
        else:
            values[4] = None
        values[6] = datetime.datetime.strptime(values[6], "%H.%M.%S")

        trust = Trust(values[0], values[1], int(values[2]), values[3], values[4],
        bool(values[5]), values[6], values[7], values[8].rstrip('\r\n'))
        db.session.add(trust)
        db.session.commit()

def store_unit_to_gps(file):
    file.readline()
    for row in file:
        values = row.split(',')
        unit_to_gps = UnitToGPSMapping(values[0], values[1].rstrip('\r\n'))

        db.session.add(unit_to_gps)
        db.session.commit()

def import_schedule(filename, table_name):
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
    else:
        print "Not a valid table name"

    f.close()

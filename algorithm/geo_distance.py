from math import sin, cos, sqrt, atan2, radians
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

from models import *


def calculateDist(coord1, coord2):
    # approximate radius of earth in km
    R = 6373.0

    coord1['latitude'] = radians(coord1['latitude'])
    coord1['longitude'] = radians(coord1['longitude'])
    coord2['latitude'] = radians(coord2['latitude'])
    coord2['longitude'] = radians(coord2['longitude'])

    dlon = coord2['longitude'] - coord1['longitude']
    dlat = coord2['latitude'] - coord1['latitude']

    a = sin(dlat / 2)**2 + cos(coord1['latitude'])\
        * cos(coord2['latitude']) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = abs(R * c)

    return distance


# Queries the db to find the long and lat of
# a tiploc
def findLongLat(tiploc):
    result = db.session.query(GeographicalLocation).\
        filter(GeographicalLocation.tiploc == tiploc).limit(1)
    return result[0].as_dict()


# Takes 2 tiplocs as parameters and calculates
# the distance between both
def calculateDistance(t1, t2):
    coord1 = findLongLat(t1)
    coord2 = findLongLat(t2)
    return calculateDist(coord1, coord2)

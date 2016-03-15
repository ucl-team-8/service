from math import sin, cos, sqrt, atan2, radians
import globals
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

from models import *


def calculateDist(coord1, coord2):
    try:
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
    except:
	return globals.tolerance['distance'] + 1

# Queries the db to find the long and lat of
# a tiploc
def findLongLat(tiploc):
    globals.db_lock.acquire()
    result = db.session.query(GeographicalLocation).\
        filter(GeographicalLocation.tiploc == tiploc).limit(1)
    globals.db_lock.release()
    try:
        return result[0].as_dict()
    except:
        return {}


# Takes 2 tiplocs as parameters and calculates
# the distance between both
def calculateDistance(t1, t2):
    coord1 = findLongLat(t1)
    coord2 = findLongLat(t2)
    return calculateDist(coord1, coord2)

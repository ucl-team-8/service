# File with all of the globals
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
import threading
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

from models import *

# Currently only stored in memory, will also store in
# database
global segments
segments = []

# Lock for accessing segment
global lock
lock = threading.RLock()


class Segment:
    def __init__(self):
        self.unit = ''
        self.cif_uid = ''
        self.gps_car_id = ''
        self.headcode = ''
        self.matching = []

    def __repr__(self):
        string = 'Segment: unit= {0}'.format(self.unit)
        string += ', gps_car_id= {0}'.format(self.gps_car_id)
        string += ', cif_uid= {0}'.format(self.cif_uid)
        string += ', headcode= {0}'.format(self.headcode)
        string += ', matching= {0}'.format(self.matching)
        return string

    def getUnitFromCarId(self, gps_car_id):
        result = db.session.query(UnitToGPSMapping).filter(
            UnitToGPSMapping.gps_car_id == gps_car_id)
        try:
            return result[0].as_dict()['unit']
        except:
            return ''

    def gps(self, gps_report):
        self.gps_car_id = gps_report['gps_car_id']
        self.unit = self.getUnitFromCarId(gps_report['gps_car_id'])
        self.matching.append({
            'gps': gps_report,
            'trust': None,
            'dist_err': None,
            'time_error': None
        })


# Time in seconds and distance in km
global tolerance
tolerance = {'time': 10 * 60 * 60, 'distance': 10}

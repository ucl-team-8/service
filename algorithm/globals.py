# File with all of the globals
# TODO: How do you get cif_uid from headcode?
import db_queries
import threading
import datetime

# Currently only stored in memory, will also store in
# database
global segments
segments = []

# This is to how many matches in matching
# the algorithm looks back at when trying
# to match a trust report to a gps report
global backmatches
backmatches = 5

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

    def gps(self, gps_report):
        self.gps_car_id = gps_report['gps_car_id']
        self.unit = db_queries.getUnitFromCarId(gps_report['gps_car_id'])
        self.matching.append({
            'gps': gps_report,
            'trust': None,
            'dist_error': None,
            'time_error': None
        })

    def trust(self, trust_report):
        self.headcode = trust_report['headcode']
        self.matching.append({
            'gps': None,
            'trust': trust_report,
            'dist_error': None,
            'time_error': None
        })


# Time in seconds and distance in km
global tolerance
tolerance = {
    'time': datetime.timedelta(minutes=10),
    'distance': 10,
    'minutes': 10
}


# Determines how fast the simulation runs
global speedup
speedup = 100

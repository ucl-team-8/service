# File with all of the globals
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
backmatches = 10

# Lock for accessing segment
global lock
lock = threading.RLock()

# Lock for accessing datebase
global db_lock
db_lock = threading.RLock()


# The overall layout of how segment should look
class Segment:
    def __init__(self):
        # self.unit = None  # We do not have a unit anymore
        self.cif_uid = None
        self.gps_car_id = None
        self.headcode = None
        self.isPlanned = False
        self.remove = False
        self.matching = []

    def __repr__(self):
        string = 'Segment: gps_car_id= {0}'.format(self.gps_car_id)
        string += ', cif_uid= {0}'.format(self.cif_uid)
        string += ', headcode= {0}'.format(self.headcode)
        string += ', isplanned= {0}'.format(self.isPlanned)
        string += ', matching= {0}'.format(self.matching)
        return string

    def gps(self, gps_report):
        self.gps_car_id = gps_report['gps_car_id']
        self.matching.append({
            'gps': gps_report,
            'trust': None,
            'dist_error': None
        })

    def trust(self, trust_report):
        self.headcode = trust_report['headcode']
        self.cif_uid = db_queries.cif_uidFromHeadcode(self.headcode)
        self.matching.append({
            'gps': None,
            'trust': trust_report,
            'dist_error': None
        })


# Time in seconds and distance in km
global tolerance
tolerance = {
    'time': datetime.timedelta(minutes=10),
    'distance': 5,
    'minutes': 10
}

# Represents the amount of minimum matching
# stops you need for a segment to become
# 'valuable' where valuable means that we can
# trust it to be an actual segment
global min_matching
min_matching = 3

# The maximum time that can be between 2 segment
# for interpolation
global min_time
min_time = datetime.timedelta(minutes=30)

# Determines how fast the simulation runs
global speedup
speedup = 5000

# The amount of threads in the threadpool
# that add events to the segments
global workers
workers = 5

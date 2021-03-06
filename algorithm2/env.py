import threading
from datetime import datetime

# effectively replaces datetime.now() since we simulate the passing of time
global now
now = datetime.fromtimestamp(0) # initialise with epoch time

# minutes events are stored in cache
# this is bigger so we can match a report that occurred some time ago, but the
# system only received it now
retention_minutes = 30

# maximum minutes difference for events to match at the same tiploc
within_minutes = 5

# the maximum minutes two matchings can overlap by
max_overlap = 5

# minutes between running the service matching algorithm
matcher_interval = 30

# the average of mean_time_error for planned (allocated) services as can be
# seen at: https://docs.google.com/spreadsheets/d/135owXzmhCaDOe5XLyhkLKTc3FnH_OZTId3x_7aEtPE4/
# this sort of means that on average, trust reports come 0.55min earlier than gps
trust_delay = -0.5

def get_corrected_error(error):
    return error - trust_delay

global matchings
matchings = dict()

global matchings_lock
matchings_lock = threading.RLock()

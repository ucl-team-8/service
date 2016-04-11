from datetime import datetime

# effectively replaces datetime.now() since we simulate the passing of time
global now
now = datetime.fromtimestamp(0) # initialise with epoch time

# minutes events are stored in cache
# this is bigger so we can match a report that occurred some time ago, but the
# system only received it now
global retention_minutes
retention_minutes = 30

# maximum minutes difference for events to match at the same tiploc
global within_minutes
within_minutes = 5

# minutes between running the service matching algorithm
global matcher_interval
matcher_interval = 30

import env
import bisect
from datetime import timedelta

# datetime difference in seconds
def sec_diff(a, b):
    return (a - b).total_seconds()

class Cache:

    def __init__(self, retention_minutes):

        self.retention_delta = timedelta(minutes=retention_minutes)

        # tiploc is key
        # value is a list of sorted instances (by time, oldest first)
        self.cache = dict()

        # tiploc is key
        # value is a list of sorted times (datetime objects), corresponding to
        # instances in self.cache
        # e.g. self.cache_times[3] is the time self.cache[3] event occurred
        self.cache_times = dict()

    def add(self, tiploc, time, instance):

        if not tiploc: return

        if tiploc not in self.cache:
            self.cache[tiploc] = list()
            self.cache_times[tiploc] = list()
        else:
            self.__clean_old(tiploc)

        instances = self.cache[tiploc]
        times = self.cache_times[tiploc]
        index = bisect.bisect_right(self.cache_times[tiploc], time)

        instances.insert(index, instance)
        times.insert(index, time)

    # gets all the events that happened at tiploc within specified minutes of
    # the given time 
    def get_within(self, tiploc, time, minutes):

        if tiploc not in self.cache:
            return []

        seconds = minutes * 60
        times = self.cache_times[tiploc]
        length = len(times)
        i = length - 1

        while i >= 0 and abs(sec_diff(times[i], time)) > seconds:
            i -= 1
        end = i + 1

        if end == 0:
            return []

        while i >= 0 and abs(sec_diff(times[i], time)) <= seconds:
            i -= 1
        start = i + 1

        return self.cache[tiploc][start:end]

    def __clean_old(self, tiploc):

        times = self.cache_times[tiploc]
        length = len(times)
        i = 0

        while i < length and env.now - times[i] > self.retention_delta:
            i += 1

        # avoid making a copy if there are no changes
        if i != 0:
            self.cache_times[tiploc] = self.cache_times[tiploc][i:]
            self.cache[tiploc] = self.cache[tiploc][i:]

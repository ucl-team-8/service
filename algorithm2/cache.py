import env
import bisect
from datetime import timedelta
from utils import diff_seconds

class Cache:
    """Caches reports for a given length of time (retention_minutes).

    Very efficiently finds cached reports at a tiploc within a given time
    interval. It uses a dictionary with tiploc as key and a sorted list of
    reports as a value, so retrieval of reports at a tiploc is O(1).

    """

    def __init__(self, retention_minutes):

        # store a timedelta for use in comparison later
        self.retention_delta = timedelta(minutes=retention_minutes)

        # tiploc is key
        # value is a list of sorted reports (by time, oldest first)
        self.reports = dict()

        # tiploc is key
        # value is a list of sorted datetime objects, corresponding to
        # reports in self.reports
        # e.g. self.timestamps[3] is the time self.reports[3] event occurred
        self.timestamps = dict()

    def add(self, tiploc, time, report):

        # do nothing in case tiploc is empty string
        if not tiploc: return

        # in case tiploc is not in dictionary yet, create it
        if tiploc not in self.reports:
            self.reports[tiploc] = list()
            self.timestamps[tiploc] = list()
        # otherwise, if it already exists, delete old reports (older than
        # retention_minutes)
        else:
            self.__clean_old(tiploc)

        reports = self.reports[tiploc]
        times = self.timestamps[tiploc]
        # bisect finds the index in a sorted list where the item can be
        # inserted while keeping the list sorted
        index = bisect.bisect_right(self.timestamps[tiploc], time)

        reports.insert(index, report)
        times.insert(index, time)

    def get_within(self, tiploc, time, minutes):
        """Returns all reports at a tiploc that occurred within the given
        minutes of the given time.
        """

        if tiploc not in self.reports:
            return []

        seconds = minutes * 60
        times = self.timestamps[tiploc]
        length = len(times)
        i = length - 1

        while i >= 0 and abs(diff_seconds(times[i], time)) > seconds:
            i -= 1
        end = i + 1

        if end == 0:
            return []

        while i >= 0 and abs(diff_seconds(times[i], time)) <= seconds:
            i -= 1
        start = i + 1

        return self.reports[tiploc][start:end]

    def __clean_old(self, tiploc):
        """Removes reports at tiploc that occurred at tiploc later then
        retention_minutes
        """

        times = self.timestamps[tiploc]
        length = len(times)
        i = 0

        while i < length and env.now - times[i] > self.retention_delta:
            i += 1

        # avoid making a copy if there are no changes
        if i != 0:
            self.timestamps[tiploc] = self.timestamps[tiploc][i:]
            self.reports[tiploc] = self.reports[tiploc][i:]

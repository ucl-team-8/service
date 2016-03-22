# This file is executed by a cleaning
# thread every x amount of time.
# It moves segments, that have not been
# updated in a while from the segments
# variable to the old_segments variable.
# This should make the algorithm a bit more
# efficient as it has to do less processing
# on the segments.

from time import sleep
import threading
import datetime
import globals


# Gets the time for a match
def getTimeFromMatching(match):
    if match['gps'] is not None:
        return match['gps']['event_time']
    return match['trust']['event_time']


# Checks if a segment is considered
# to be old.
def checkIfOld(segment, current_time):
    segment.matching.sort(key=lambda x: getTimeFromMatching(x), reverse=False)
    if len(segment.matching) > 0:
        time_diff = abs(
            getTimeFromMatching(segment.matching[-1]) -
            current_time
        )
        if time_diff > globals.is_old:
            return True
    return False


# Moves a segment from the segments
# variable to the old_segments var
def moveToOldSegment(segment):
    globals.old_segments[segment.id] = segment
    del globals.segments[segment.id]


# Gets the current time of the simulation
def getCurrentTime(simulation):
    gps = len(simulation.records['gps'])
    trust = len(simulation.records['trust'])
    if gps > 0 and trust > 0:
        return min([simulation.records['gps'][0]['event_time'],
            simulation.records['trust'][0]['event_time']])
    elif gps > 0:
        return simulation.records['gps'][0]['event_time']
    elif trust > 0:
        return simulation.records['trust'][0]['event_time']
    return datetime.datetime.now()


class Cleaner(threading.Thread):
    def __init__(self, simulation):
        threading.Thread.__init__(self)
        self.simulation = simulation
        self.sleep_time = globals.clean_time.total_seconds() / simulation.speed
        self.stopped = False

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            sleep(self.sleep_time)
            globals.lock.acquire()
            current_time = getCurrentTime(self.simulation)
            for segment in globals.segments.values():
                if checkIfOld(segment, current_time):
                    moveToOldSegment(segment)
            globals.lock.release()



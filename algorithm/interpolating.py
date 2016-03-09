# Performs the interpolating, every time a trust report is added
# to the segments to check if they have certain properties
# (see readme interpolating)

# TODO: We can probably decrease how often we run this code
# instead of running it every time a trust_report is added
# to the segments, it might be better to run it every 10 min?

import globals


# For a particular segment, counts how
# many matches there are
def countMatching(segment):
    count = 0
    for match in segment.matching:
        if match['gps'] is not None and match['trust'] is not None:
            count += 1
    return count

# Gets all of the segments with a particular unit
def getSegmentsWithUnit(unit):
    globals.lock.acquire()
    segments = []
    for segment in globals.segments:
        if segment.unit == unit:
            segments.append(segment)
    globals.lock.release()
    return segments

# Gets the time of the report
def getReportTime(report):
    if report['gps'] is not None:
        return report['gps']['event_time']
    else:
        return report['trust']['event_time']

def removeSegments():
    globals.lock.acquire()
    for i in range(0, len(globals.segments)):
        if globals.segments[i].remove:
            del globals.segments[i]
    globals.lock.release()


# Combines the segments from i to j and
# store all of the reports in i
def combineSegments(segments, i, j):
    globals.lock.acquire()
    for k in range(i + 1, j):
        segments[i].matching.extend(segments[k].matching)
        segments[k].remove = True
    segments[i].matching.sort(key=lambda x: getReportTime(x), reverse=False)
    globals.lock.release()


# Helper function for join segments that joins
# together segments as illustrated by figure 2
# in the readme
def joinSegmentsHelper(segments, i):
    imatching = countMatching(segments[i])
    if imatching < globals.min_matching:
        return
    stops_in_between = 0
    # Loops through the lookaheads
    for j in range(i + 1, len(segments)):
        jmatching = countMatching(segments[j])
        if segments[i].gps_car_id == segments[j].gps_car_id:
            combineSegments(segments, i, j)
        else:
            stops_in_between += jmatching
            if stops_in_between > globals.min_matching:
                return

# Joins the segments together, as discussed in the readme
def joinSegments(segments):
    # Sort them in reversed order such that we can go through them
    # backwards
    segments.sort(key=lambda x: getReportTime(x.matching[-1]), reverse=True)
    # We don't want to have i to be the last segment
    for i in range(0, len(segments) - 1):
        if segments[i].gps_car_id == segments[i + 1].gps_car_id:
            # Join them together because they have the same gps and unit
            globals.lock.acquire()
            segments[i].matching.extend(segments[i + 1].matching)
            segments[i].matching.sort(key=lambda x: getReportTime(x), reverse=False)
            segments[i + 1].remove = True
            globals.lock.release()
        else:
            joinSegmentsHelper(segments, i)
        removeSegments()


# Checks if there are 2 rolling stock that might be running
# the given service by checking if there are potentially other
# segments with no unit that are running the same service
# and adds the trust reports to it
def runningSameService(unit):
    pass

def interpolate(unit):
    segments = getSegmentsWithUnit(unit)
    joinSegments(segments)
    runningSameService(unit)



# This file is responsible for adding trust
# reports to the segments

# TODO: Can we use planned_pass?
# TODO: Use filterByDiagrams -> The variable predicted in the trust
# report is set to true if filterByDiagrams returns true
# TODO: Give preference to the same event type?

import geo_distance
import interpolating
import db_queries
import datetime
import globals


# We only want to look at the segments with the
# same headcode as the trust so this filters out
# the ones that don't have the same headcode
def filterSegmentsByHeadcode(trust):
    potential_segments = []
    globals.lock.acquire()
    for segment in globals.segments:
        if segment.headcode == '':
            potential_segments.append(segment)
        elif segment.headcode == trust['headcode']:
            potential_segments.append(segment)
    globals.lock.release()
    return potential_segments


# This is the first layer, filtering segments
# by time and distance
def filterPotentialSegments(segments, trust):
    potential_segments = []
    for segment in segments:
        for i in range(-globals.backmatches, 0):
            try:
                if (segment.matching[i]['gps'] is not None) and\
                        (segment.matching[i]['trust'] is None):
                    time_error = abs(
                        segment.matching[i]['gps']['event_time'] -
                        trust['event_time'])
                    if time_error < globals.tolerance['time']:
                        dist_error = geo_distance.calculateDistance(
                            segment.matching[i]['gps']['tiploc'], trust['tiploc'])
                        if dist_error < globals.tolerance['distance']:
                            potential_segments.append(segment)
                            break
            except:
                pass # Do nothing
    return potential_segments




# The second layer that filters the potential segments
# again and finds segments that it is supposed to run
# using the genius allocations (named schedule in the db)
def filterByGeniusAllocations(segments, trust):
    potential_segments = []
    for segment in segments:
        if segment.isPlanned or db_queries.isPlanned(segment.unit, trust['headcode']):
            potential_segments.append(segment)
    if len(potential_segments) > 0:
        return potential_segments
    return segments


# Checks if there is a pathing or engineering
# allowance for a stop
def getExtraTime(stop):
    extra_time = 0
    if stop['pathing_allowance'] is not None:
        extra_time += stop['pathing_allowance']
    if stop['engineering_allowance'] is not None:
        extra_time += stop['engineering_allowance']
    return extra_time


# Since a stop has either a arrive_time,
# depart_time and pass_time, this function
# extracts the right one
def getTimeFromStop(stop, trust):
    if (stop['arrive_time'] is not None) and\
            (trust['event_type'] == 'A'):
        return stop['arrive_time']
    elif(stop['depart_time'] is not None) and\
            (trust['event_type'] == 'D'):
        return stop['depart_time']
    elif(stop['pass_time'] is not None) and\
            (trust['event_type'] == 'P'):
        return stop['pass_time']
    elif stop['arrive_time'] is not None:
        return stop['arrive_time']
    elif stop['depart_time'] is not None:
        return stop['depart_time']
    return stop['pass_time']


# gets the time difference in minutes
# between 2 datetime.time objects
def time_difference(start, end):
    reverse = False
    if start > end:
        start, end = end, start
        reverse = True

    delta = (end.hour - start.hour) * 60 + end.minute - start.minute +\
            (end.second - start.second) / 60.0
    if reverse:
        delta = 24 * 60 - delta
    return delta


# Checks if the trust event is one that was
# supposed to happen according to the diagrams
def isPredictedReport(trust):
    diagram_stops = db_queries.getDiagramStopsByHeadcode(trust['headcode'])
    for stop in diagram_stops:
        if stop['tiploc'] == trust['tiploc']:
            extra_time = getExtraTime(stop)
            time = getTimeFromStop(stop, trust)
            time_diff = time_difference(time, trust['event_time'].time())
            time_diff -= extra_time
            if(abs(time_diff) < globals.tolerance['minutes']):
                return True
    return False


# Chooses which one is the better sequence
# returns true is current is better than best
def isBetterSegment(segment, current, best):
    currentValue = current['matching'] + current['seq_respected']
    bestValue = best['matching'] + best['seq_respected']

    # >= than because initially every segment has
    # 0 matching
    if currentValue >= bestValue:
        best['segment'] = segment
        best['matching'] = current['matching']
        best['seq_respected'] = current['seq_respected']


# from the list of filtered segments, this function
# chooses the best one according to 2 factors,
# the first is how accurately the seq are
# the second by how many matches there are
def chooseBestSegment(segments, trust):
    best = {'matching': 0, 'seq_respected': 0, 'segment': None}
    for segment in segments:
        current = {'matching': 0, 'seq_respected': 0, 'seq': 0}
        for match in segment.matching:
            if (match['gps'] is not None) and\
                    (match['trust'] is not None):
                current['matching'] += 1
                if match['trust']['seq'] < current['seq']:
                    current['seq_respected'] += 1
                    current['seq'] = match['trust']['seq']
        isBetterSegment(segment, current, best)
    return best['segment']


# Creates a new segment and stores
# it in the global
def createNewSegment(trust):
        segment = globals.Segment()
        segment.trust(trust)
        globals.segments.append(segment)


def setBestStop(best, dist_error, time_error, match):
    best['dist_error'] = dist_error
    best['time_error'] = time_error
    best['match'] = match


# Gets the gps report in a particular segment
# for a trust report and then adds trust report
# to that stop
# the with_seq flag determines if the function takes
# seq in consideration
def getBestStop(segment, trust, with_seq):
    best = {
        'match': None,
        'time_error': datetime.timedelta(days=1),
        'dist_error': 1000000  # km
    }
    last_seq = 0
    for match in segment.matching:
        if(match['gps'] is not None) and\
                (match['trust'] is None):
            dist_error = geo_distance.calculateDistance(
                match['gps']['tiploc'], trust['tiploc'])
            time_error = abs(match['gps']['event_time'] - trust['event_time'])
            if(dist_error < best['dist_error']) and\
                    (time_error < best['time_error']):
                if with_seq and (trust['seq'] > last_seq):
                    setBestStop(best, dist_error, time_error, match)
                elif not with_seq:
                    setBestStop(best, dist_error, time_error, match)
        elif match['trust'] is not None:
            last_seq = match['trust']['seq']

    if best['match'] is not None:
        best['match']['trust'] = trust
        best['match']['dist_error'] = best['dist_error']
        if segment.headcode == '':
            segment.headcode = trust['headcode']
            segment.cif_uid = db_queries.cif_uidFromHeadcode(trust['headcode'])
        return True
    elif with_seq:
        if not getBestStop(segment, trust, False):
            createNewSegment(trust)


# Adds the trust report to a segment
def addTrust(trust_report):
    trust_report['predicted'] = isPredictedReport(trust_report)
    segments = filterSegmentsByHeadcode(trust_report)
    segments = filterPotentialSegments(segments, trust_report)
    segments = filterByGeniusAllocations(segments, trust_report)

    segment = chooseBestSegment(segments, trust_report)
    globals.lock.acquire()
    if segment is None:
        createNewSegment(trust_report)
    else:
        segment.isPlanned = db_queries.isPlanned(segment.unit, trust_report['headcode'])
        getBestStop(segment, trust_report, True)
    globals.lock.release()
    interpolating.interpolate(trust_report['headcode'])

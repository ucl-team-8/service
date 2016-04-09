# Performs the interpolating, every time a trust report is added
# to the segments to check if they have certain properties
# (see readme interpolating)

# TODO: We can probably decrease how often we run this code
# instead of running it every time a trust_report is added
# to the segments, it might be better to run it every 10 min?

import geo_distance
import filter_gps
import db_queries
import socket_io
import globals


# For a particular segment, counts how
# many matches there are
def countMatching(segment):
    count = 0
    for match in segment.matching:
        if match['gps'] is not None and match['trust'] is not None:
            count += 1
    return count


# Gets all of the segments with a particular headcode
def getSegmentsWithHeadcode(headcode):
    globals.lock.acquire()
    segments = []
    for segment in globals.segments.values():
        if segment.headcode == headcode:
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
    for key, segment in globals.segments.items():
        if segment.remove:
            socket_io.emitSegment('delete', key)
            del globals.segments[key]


# Removes any gps reports from the
# segment because we do not want
# different gps_car_id's in the same
# segment
def removeGPSReports(segment, gps_car_id):
    # Making sure that we do not add
    # the gps_report to this segment again
    segment.gps_car_id = gps_car_id
    length = len(segment.matching)
    i = 0
    while i < length:
        match = segment.matching[i]
        if match['gps'] is not None:
            filter_gps.addGPS(match['gps'])
            if match['trust'] is None:
                del segment.matching[i]
                length -= 1
                i -= 1
            else:
                match['gps'] = None
        i += 1


# Combines the segments from i to j and
# store all of the reports in i
def combineSegments(segments, i, j):
    for k in range(i + 1, j + 1):
        if segments[k].gps_car_id != segments[i].gps_car_id:
            removeGPSReports(segments[k], segments[i].gps_car_id)
        segments[i].matching.extend(segments[k].matching)
        segments[k].remove = True
    segments[i].matching.sort(key=lambda x: getReportTime(x), reverse=False)
    socket_io.emitSegment('update', segments[i])


# Sorts all of the matching in the
# segments
def sortSegments(segments):
    for segment in segments:
        segment.matching.sort(key=lambda x: getReportTime(x), reverse=False)


# Helper function for join segments that joins
# together segments as illustrated by figure 2
# in the readme
def joinSegmentsHelper(segments, i):
    imatching = countMatching(segments[i])
    if imatching < globals.min_matching:
        # The segment is not long enough to be 'trusted'
        return
    stops_in_between = 0
    # Loops through the lookaheads
    for j in range(i + 1, len(segments)):
        jmatching = countMatching(segments[j])
        if segments[i].gps_car_id == segments[j].gps_car_id:
            time_diff = abs(getReportTime(segments[i].matching[-1]) -
                getReportTime(segments[j].matching[-1]))
            if time_diff < globals.min_time:
                combineSegments(segments, i, j)
        else:
            stops_in_between += jmatching
            if stops_in_between > globals.min_matching:
                return


# Joins the segments together, as discussed in the readme
def joinSegments(segments):
    # Sort them in reversed order such that we can go through them
    # backwards
    globals.lock.acquire()
    sortSegments(segments)
    segments.sort(key=lambda x: getReportTime(x.matching[-1]), reverse=True)
    # We don't want to have i to be the last segment
    for i in range(0, len(segments) - 1):
        if segments[i].gps_car_id == segments[i + 1].gps_car_id:
            # Join them together because they have the same gps and headcode
            combineSegments(segments, i, i + 1)
        else:
            joinSegmentsHelper(segments, i)
        removeSegments()
    globals.lock.release()


# Checks if a gps report matches a
# trust report
def isMatching(gps, trust):
    time_error = abs(gps['event_time'] - trust['event_time'])
    if time_error < globals.tolerance['time']:
        dist_error = geo_distance.calculateDistance(
            gps['tiploc'], trust['tiploc'])
        if dist_error < globals.tolerance['distance']:
            return True
    return False


# Finds the next index in the empty_matching
# list that is within the time constraint
def findNextIndex(match, empty_matching, next_index):
    if next_index < len(empty_matching):
        time_error = abs(getReportTime(match) - getReportTime(empty_matching[next_index]))
        while time_error > globals.tolerance['time'] and\
                next_index < len(empty_matching):
            time_error = abs(getReportTime(match) - getReportTime(empty_matching[next_index]))
            next_index += 1
        return next_index
    return len(empty_matching) - 1


# Checks if you have enough potential_matches and
# if you do, it adds those to the segment
def checkPotentialMatches(segment, potential_matches):
    if len(potential_matches) > globals.min_matching:
        globals.lock.acquire()
        segment.headcode = potential_matches[0]['trust']['headcode']
        segment.cif_uid = db_queries.cif_uidFromHeadcode(segment.headcode)
        for match in potential_matches:
            segment.matching[match['index']]['trust'] = match['trust']
        socket_io.emitSegment('update', segment)
        globals.lock.release()


# Checks a segment with both gps_car_id and headcode
# and a segment without a headcode and see if they are both
# potentially running the same service
def matchingSegments(segment, empty_segment):
    globals.lock.acquire()
    potential_matches = []
    next_index = 0
    segment.matching.sort(key=lambda x: getReportTime(x), reverse=False)
    empty_segment.matching.sort(key=lambda x: getReportTime(x), reverse=False)
    for match in segment.matching:
        if match['trust'] is not None:
            next_index = findNextIndex(match, empty_segment.matching, next_index)
            for i in range(next_index, len(empty_segment.matching)):
                if isMatching(empty_segment.matching[i]['gps'], match['trust']):
                    next_index = i + 1
                    potential_matches.append({
                        'index': i,
                        'trust': match['trust']
                    })
    checkPotentialMatches(empty_segment, potential_matches)
    globals.lock.release()


# Checks if a report in a match happens between
# the first and last event in the segment
def inTimeLimit(segment, trust):
    # We know that segment is sorted
    after = trust['event_time'] > getReportTime(segment.matching[0])
    before = trust['event_time'] < getReportTime(segment.matching[-1])
    return before and after


# Deletes all of the matches in the
# matches variable from the given segment
def deleteReports(segment):
    segment.matching = filter(lambda x: not x['delete'],
        segment.matching[-globals.backmatches:]) + segment.matching[:-globals.backmatches]
    if len(segment.matching) == 0:
        socket_io.emitSegment('delete', segment.id)
        del globals.segments[segment.id]
    else:
        socket_io.emitSegment('update', segment)


# If you have enough empty matches, joins them
def checkEmptyMatches(segment, empty_segment, potential_matches):
    if len(potential_matches) > globals.min_matching:

        for i, match in enumerate(potential_matches):
            if 'index' in match:  # It can match to a gps
                dist_error = geo_distance.calculateDistance(
                    match['trust']['tiploc'], segment.matching[match['index']]['gps']['tiploc'])
                segment.matching[match['index']]['trust'] = match['trust']
                segment.matching[match['index']]['dist_error'] = dist_error
                del potential_matches[i]
        for match in potential_matches:
            segment.matching.append({
                'dist_err': None,
                'gps': None,
                'trust': match['trust']
            })
        socket_io.emitSegment('update', segment)
        deleteReports(empty_segment)


# We get a segment with both a gps_car_id
# and a headcode in the segment parameter.
# On the other hand, the empty_segment does
# not have a gps_car_id but it does have the
# same headcode. This function tries to insert
# the trust reports in the empty_segment into
# the segment parameter

# We go over the matching and see if they fall within the time
# interval. If they do, we try to find a match.
# If we do (increment min_matching and store match)
# else if we do not, we try to find a gps report that
# already has a match (and increment min_matching)
# If we have more min_matching, we add the matches
# and append the non matching
def matchingEmptyTrust(segment, empty_segment):
    globals.lock.acquire()
    segment.matching.sort(key=lambda x: getReportTime(x), reverse=False)
    empty_segment.matching.sort(key=lambda x: getReportTime(x), reverse=False)
    potential_matches = []
    for i in range(-globals.backmatches, 0):
        try:
            match = segment.matching[i]
        except IndexError:
            continue
        for j in range(-globals.backmatches, 0):
            try:
                empty_match = empty_segment.matching[j]
            except IndexError:
                continue
            empty_match['delete'] = False
            if match['gps'] is not None:
                if match['trust'] is None:
                    if isMatching(match['gps'], empty_match['trust']):
                        potential_matches.append({
                            'index': i,
                            'trust': empty_match['trust']
                        })
                        empty_match['delete'] = True
                else:  # If the gps already has a matching trust
                    # The matching can still be inserted
                    if isMatching(match['gps'], empty_match['trust']):
                        potential_matches.append({
                            'trust': empty_match['trust']
                        })
                        empty_match['delete'] = True

    checkEmptyMatches(segment, empty_segment, potential_matches)
    globals.lock.release()


# Finds all of the segments with a
# particular headcode, then splits the
# ones that have a gps_car_id and
# the others that do not.
def insertEmptyMatchingTrust(headcode):
    segments = getSegmentsWithHeadcode(headcode)
    empty_segments = filter(lambda x: x.gps_car_id is None, segments)
    segments = filter(lambda x: x.gps_car_id is not None, segments)
    for segment in segments:
        for empty_segment in empty_segments:
            matchingEmptyTrust(segment, empty_segment)


# Checks if there are 2 rolling stock that might be running
# the given service by checking if there are potentially other
# segments with no headcode that are running the same service
# and adds the trust reports to it
def runningSameService(headcode):
    segments = getSegmentsWithHeadcode(headcode)
    empty_segments = getSegmentsWithHeadcode(None)
    for segment in segments:
        for empty_segment in empty_segments:
            matchingSegments(segment, empty_segment)


def interpolate(headcode):
    segments = getSegmentsWithHeadcode(headcode)
    joinSegments(segments)
    runningSameService(headcode)
    insertEmptyMatchingTrust(headcode)

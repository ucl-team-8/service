# File that is responsible for adding gps_reports
# to the segments

import geo_distance
import db_queries
import socket_io
import datetime
import globals


# Checks the time difference between the segment and checks
# if the it closer to the gps_report than the current
# closest
def checkTimeDiff(segment, gps_report, closest):
    time_diff = None
    if segment.matching[-1]['gps'] is not None:
        time_diff = abs(segment.matching[-1]['gps']['event_time'] -
                gps_report['event_time'])
    if segment.matching[-1]['trust'] is not None:
        temp_diff = abs(segment.matching[-1]['trust']['event_time'] -
                gps_report['event_time'])
        if time_diff is None:
            time_diff = temp_diff
        elif temp_diff < time_diff:
            time_diff = temp_diff
    if time_diff < closest['time_diff']:
        closest['segment'] = segment
        closest['time_diff'] = time_diff


# Gets the time from either report
# in the match
def getTimeFromMatching(match):
    if match['gps'] is not None:
        return match['gps']['event_time']
    return match['trust']['event_time']


# Finds the segment with the reports
# that happened near the gps_report
def findClosestSegment(segments, gps_report):
    closest = {'segment': None, 'time_diff': datetime.timedelta(days=1)}
    # First checks empty segments because it might be a rolling stock starting to run
    # another service
    for segment in segments.values():
        if segment.gps_car_id is None:
            segment.matching.sort(key=lambda x: x['trust']['event_time'], reverse=False)
            checkTimeDiff(segment, gps_report, closest)
    if closest['segment'] is None:
        for segment in segments.values():
            segment.matching.sort(
                    key=lambda x: getTimeFromMatching(x), reverse=False)
            if segment.gps_car_id == gps_report['gps_car_id']:
                checkTimeDiff(segment, gps_report, closest)
    return closest['segment']


# Finds the closest segment with the same gps_car_id
def findClosestGPSSegment(segments, gps_report):
    closest = {'segment': None, 'time_diff': datetime.timedelta(days=1)}
    for segment in segments.values():
        segment.matching.sort(
                key=lambda x: getTimeFromMatching(x), reverse=False)
        if segment.gps_car_id == gps_report['gps_car_id']:
            checkTimeDiff(segment, gps_report, closest)
    return closest['segment']


# Checks if this gps report is a potential
# match with a trust report in the segment
# and adds the gps report to the trust if there is
# a match, then returns a boolean which shows
# if it found a match
def checkNonMatchingTrust(segment, gps_report):
    closest = {
        'match': None,
        'time_error': datetime.timedelta(days=1),
        'dist_error': 1000000
    }
    for match in segment.matching:
        if (match['trust'] is not None) and (match['gps'] is None):
            time_error = abs(
                match['trust']['event_time'] - gps_report['event_time'])
            dist_error = geo_distance.calculateDistance(
                match['trust']['tiploc'], gps_report['tiploc']
            )
            if dist_error < globals.tolerance['distance']\
                    and time_error < globals.tolerance['time']:
                if dist_error < closest['dist_error'] and\
                        time_error < closest['time_error']:
                    closest['match'] = match
                    closest['dist_error'] = dist_error
                    closest['time_error'] = time_error
    if closest['match'] is not None:
        closest['match']['gps'] = gps_report
        closest['match']['dist_error'] = dist_error
        if segment.gps_car_id is None:
           segment.gps_car_id = gps_report['gps_car_id']
           segment.isPlanned = db_queries.isPlanned(segment.gps_car_id, segment.headcode)
        socket_io.emitSegment('update', segment)
        return True
    return False


# This function adds the gps report to a segment
def addGPS(gps_report):
    if gps_report is None:
        return
    globals.lock.acquire()
    segment = findClosestSegment(globals.segments, gps_report)
    if segment is None:
        globals.createNewSegment(gps_report)
    elif not checkNonMatchingTrust(segment, gps_report):
        segment = findClosestGPSSegment(globals.segments, gps_report)
        if segment is None:
            globals.createNewSegment(gps_report)
        else:
            segment.matching.append({
                'gps': gps_report,
                'trust': None,
                'dist_error': None
            })
            socket_io.emitSegment('update', segment)
    globals.lock.release()

# File that is reponsible for adding gps_reports
# to the segments

# TODO: Backtracking to see if it can join
# segments
# TODO: In checkNonMatchingTrust should it also check
# trust reports that have a match to see if this is a potential
# closer match?
# TODO: Should checkNonMatchingTrust choose the closest trust?

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import geo_distance
import datetime
import globals
import time
import os


# Finds the segment with the reports
# that happened near the gps_report
def findClosestSegment(segments, gps_report):
    closest = {'segment': None, 'time_diff': datetime.timedelta(days=1)}
    for segment in segments:
        if segment.gps_car_id == gps_report['gps_car_id']:
            time_diff = abs(segment.matching[-1]['gps']['event_time'] -
                            gps_report['event_time'])
            if time_diff < closest['time_diff']:
                closest['segment'] = segment
                closest['time_diff'] = time_diff
    return closest['segment']


# Checks if this gps report is a potential
# match with a trust report in the segment
def checkNonMatchingTrust(segment, gps_report):
    for match in segment.matching:
        if (match['trust'] is not None) and (match['gps'] is None):
            time_error = abs(
                match['trust']['event_time'] - gps_report['event_time'])
            dist_error = geo_distance.calculateDistance(
                match['trust']['tiploc'], gps_report['tiploc']
            )
            if dist_error < globals.tolerance['distance']\
                    and time_err < globals.tolerance['time']:
                match['gps'] = gps_report
                match['dist_error'] = dist_err
                match['time_error'] = time_err
                return True
    return False


# This function adds the gps report to a segment
def addGPS(gps_report):
    potential_segments = []
    for segment in globals.segments:
        if segment.gps_car_id == gps_report['gps_car_id']:
            potential_segments.append(segment)

    segment = findClosestSegment(potential_segments, gps_report)
    if segment is None:
        segment = globals.Segment()
        segment.gps(gps_report)
        globals.segments.append(segment)

    elif not checkNonMatchingTrust(segment, gps_report):
        segment.matching.append({
            'gps': gps_report,
            'trust': None,
            'dist_error': None,
            'time_error': None
        })

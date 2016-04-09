import unittest
import os
import json
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir + '/algorithm')

import geo_distance
import db_queries

import simrealtime
import app
from models import GPS


tolerance = 0.001

coord1 = {'latitude': 52.2296756, 'longitude': 21.0122287}
coord2 = {'latitude': 52.406374, 'longitude': 16.9251681}
coord3 = {'latitude': 57.4774160525352, 'longitude': -4.46815579590345}
coord4 = {'latitude': 51.6909417951552, 'longitude': -3.40287716811208}

class TestSimulation(unittest.TestCase):

    simulation = simrealtime.SimulateRealTime(1000)

    def testFetchEvents(self):
        # Test for no events
        fetched = self.simulation.fetchEvents(GPS, None)
        self.assertIsNotNone(fetched)
        self.assertLessEqual(len(fetched), 100)

        # Test for more than one event (up to 100)
        # Is it supposed to handle 1 record? Currently Doesn't
        randRecs = [ x.as_dict() for x in app.db.session.query(GPS).filter(GPS.tiploc=='KNGX').all()]
        newFetched = self.simulation.fetchEvents(GPS, randRecs)
        self.assertLessEqual(newFetched[0]['event_time'], newFetched[1]['event_time'])

class TestEndPoints(unittest.TestCase):

    def setUp(self):
        app.app.config['TESTING'] = True
        self.testApp = app.app.test_client()

    def get(self, resource):
        return self.testApp.get(resource)

    def checkDict(self, response):
        return isinstance(json.loads(response.data), dict)

    def testSegments(self):
        response = self.get('/data/segments.json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.checkDict(response))

    def testGPS(self):
        response = self.get('/events/gps.json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.checkDict(response))

    def testTrust(self):
        response = self.get('/events/trust.json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.checkDict(response))

    def testSchedule(self):
        response = self.get('/data/schedule.json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.checkDict(response))

class TestGeoDist(unittest.TestCase):
    def test_distance1(self):
        self.assertLess(
            abs(geo_distance.calculateDist(coord1, coord2) - 278.54558935106695), tolerance
        )

    def test_distance2(self):
        self.assertLess(
            abs(geo_distance.calculateDist(coord3, coord4) - 647.259510348751), tolerance
        )

    def test_tiploc_long_lat(self):
        result = geo_distance.findLongLat('BEAULY')
        self.assertLess(abs(result['latitude'] - 57.4774160525352), tolerance)
        self.assertLess(abs(result['longitude'] - -4.46815579590345), tolerance)

    def test_calculate_distance(self):
        result = geo_distance.calculateDistance('BEAULY', 'ABCWM')
        self.assertLess(result - 647.259510348751, tolerance)


class TestDBQueries(unittest.TestCase):
    def test_isPlanned1(self):
        result = db_queries.isPlanned('82215', '5D02')
        self.assertEqual(result, True)

    def test_isPlanned2(self):
        result = db_queries.isPlanned('BN30', '5A04')
        self.assertEqual(result, False)

    def testDiagramServiceByUnit1(self):
        result = db_queries.getDiagramServiceByHeadcode('0P04')
        self.assertEqual(result['cif_uid'], 'Y58236')

    def testDiagramServiceByUnit2(self):
        result = db_queries.getDiagramServiceByHeadcode('0')
        self.assertEqual(result, None)

    def testDiagramStopsByService(self):
        temp = db_queries.getDiagramServiceByHeadcode('0P04')
        result = db_queries.getDiagramStopsByService(temp)
        station_type = result[0]['station_type']
        self.assertEqual(station_type, 'LO')

    def testGetDiagramStopsByH(self):
        result = db_queries.getDiagramStopsByHeadcode('0P04')
        station_type = result[0]['station_type']
        self.assertEqual(station_type, 'LO')

    def testcif_uidFromUnit1(self):
        result = db_queries.cif_uidFromUnitAndHeadcode('82227', '5E06')
        self.assertEqual(result, 'Y62392')

    def testcif_uidFromUnit2(self):
        result = db_queries.cif_uidFromUnitAndHeadcode('BN', '5E06')
        self.assertEqual(result, '')

    def testcif_uidFromUnit3(self):
        result = db_queries.cif_uidFromUnitAndHeadcode('BN87', '0Z00')
        self.assertEqual(result, '')

    def testcif_uidFromHeadcode1(self):
        result = db_queries.cif_uidFromHeadcode('0B02')
        self.assertEqual(result, 'Y57996')

    def testcif_uidFromHeadcode2(self):
        result = db_queries.cif_uidFromHeadcode('1A00')
        self.assertEqual(result, 'Y58484')

    def testcif_uidFromHeadcode3(self):
        result = db_queries.cif_uidFromHeadcode('0')
        self.assertEqual(result, None)


if __name__ == "__main__":
    unittest.main()

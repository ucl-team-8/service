import unittest
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir + '/algorithm')

import geo_distance
import db_queries
import datetime
import globals
import cleaner

tolerance = 0.001
coord1 = {'latitude': 52.2296756, 'longitude': 21.0122287}
coord2 = {'latitude': 52.406374, 'longitude': 16.9251681}
coord3 = {'latitude': 57.4774160525352, 'longitude': -4.46815579590345}
coord4 = {'latitude': 51.6909417951552, 'longitude': -3.40287716811208}

# Test class for cleaner
class Simulation():
    def __init__(self, gps, trust):
        self.records = {'gps': gps, 'trust': trust}

old = datetime.datetime.now() - globals.is_old
now= datetime.datetime.now()

now_dict = {'event_time': now}
old_dict = {'event_time': old}

sim1 = Simulation([now_dict], [now_dict])
sim2 = Simulation([now_dict], [old_dict])
sim3 = Simulation([old_dict], [now_dict])
sim4 = Simulation([old_dict], [old_dict])
sim5 = Simulation([old_dict], [])
sim6 = Simulation([], [now_dict])


newSegment1 = globals.Segment()
newSegment1.matching.append({'trust': {'event_time': now}, 'gps': None})

newSegment2 = globals.Segment()
newSegment2.matching.append({'gps': {'event_time': now}, 'trust': None})

oldSegment1 = globals.Segment()
oldSegment1.matching.append({'trust': {'event_time': old}, 'gps': None})

oldSegment2 = globals.Segment()
oldSegment2.matching.append({'gps': {'event_time': old}, 'trust': None})


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
        result = db_queries.isPlanned('BN09', '5D02')
        self.assertEqual(result, True)

    def test_isPlanned2(self):
        result = db_queries.isPlanned('BN30', '5A04')
        self.assertEqual(result, False)

    def testGetUnitFromCarId1(self):
        result = db_queries.getUnitFromCarId('82200')
        self.assertEqual(result, 'BN20')

    def testGetUnitFromCarId2(self):
        result = db_queries.getUnitFromCarId('82217')
        self.assertEqual(result, 'BN28')

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
        result = db_queries.cif_uidFromUnitAndHeadcode('BN21', '5E06')
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


class TestCleaner(unittest.TestCase):
    def setUp(self):
        globals.segments = {}
        globals.old_segments = {}

    def testGetCurrentTime1(self):
        time = cleaner.getCurrentTime(sim1)
        self.assertEqual(now, time)

    def testGetCurrentTime2(self):
        time = cleaner.getCurrentTime(sim2)
        self.assertEqual(old, time)

    def testGetCurrentTime3(self):
        time = cleaner.getCurrentTime(sim3)
        self.assertEqual(old, time)

    def testGetCurrentTime4(self):
        time = cleaner.getCurrentTime(sim4)
        self.assertEqual(old, time)

    def testGetCurrentTime5(self):
        time = cleaner.getCurrentTime(sim5)
        self.assertEqual(old, time)

    def testGetCurrentTime6(self):
        time = cleaner.getCurrentTime(sim6)
        self.assertEqual(now, time)

    def testMoveOldSegment(self):
        globals.segments[oldSegment1.id] = oldSegment1
        cleaner.moveToOldSegment(oldSegment1)
        self.assertEqual(len(globals.segments), 0)
        self.assertEqual(len(globals.old_segments), 1)

    def testCheckIfOld1(self):
        result = cleaner.checkIfOld(newSegment1, now)
        self.assertEqual(result, False)

    def testCheckIfOld2(self):
        result = cleaner.checkIfOld(newSegment2, now)
        self.assertEqual(result, False)

    def testCheckIfOld3(self):
        result = cleaner.checkIfOld(oldSegment1, now)
        self.assertEqual(result, True)

    def testCheckIfOld4(self):
        result = cleaner.checkIfOld(oldSegment2, now)
        self.assertEqual(result, True)


if __name__ == "__main__":
    unittest.main()

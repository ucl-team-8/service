import unittest
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir + '/algorithm')

import geo_distance
import db_queries

coord1 = {'latitude': 52.2296756, 'longitude': 21.0122287}
coord2 = {'latitude': 52.406374, 'longitude': 16.9251681}
coord3 = {'latitude': 57.4774160525352, 'longitude': -4.46815579590345}
coord4 = {'latitude': 51.6909417951552, 'longitude': -3.40287716811208}


class TestGeoDist(unittest.TestCase):
    def test_distance1(self):
        self.assertEqual(
            geo_distance.calculateDist(coord1, coord2), 278.54558935106695
        )

    def test_distance2(self):
        self.assertEqual(
            geo_distance.calculateDist(coord3, coord4), 647.259510348751
        )

    def test_tiploc_long_lat(self):
        result = geo_distance.findLongLat('BEAULY')
        self.assertEqual(result['latitude'], 57.4774160525352)
        self.assertEqual(result['longitude'], -4.46815579590345)

    def test_calculate_distance(self):
        result = geo_distance.calculateDistance('BEAULY', 'ABCWM')
        self.assertEqual(result, 647.259510348751)


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
        result = db_queries.getDiagramServiceByUnit('0P04')
        self.assertEqual(result['cif_uid'], 'Y58236')

    def testDiagramServiceByUnit1(self):
        result = db_queries.getDiagramServiceByUnit('0')
        self.assertEqual(result, None)

    def testDiagramStopsByService(self):
        temp = db_queries.getDiagramServiceByUnit('0P04')
        result = db_queries.getDiagramStopsByService(temp)
        station_type = result[0]['station_type']
        self.assertEqual(station_type, 'LO')

    def testGetDiagramStopsByUnit(self):
        result = db_queries.getDiagramStopsByUnit('0P04')
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

if __name__ == "__main__":
    unittest.main()

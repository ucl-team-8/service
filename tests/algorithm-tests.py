import unittest
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir + '/algorithm')

import filter_trust
import geo_distance

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

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python 

import unittest
from redis import Redis
from ..query import GeoHasher


class QueryTestCase(unittest.TestCase):


    def setUp(self):
        redis_client = Redis()
        self.geohasher = GeoHasher(redis_client)
        self.geohasher.add_coordinate(37.7833, -122.4167, 'SF')
        self.geohasher.add_coordinate(37.7833, -122.4667, 'SF-West')
        self.geohasher.add_coordinate(37.7833, -122.3667, 'SF-East')
        self.geohasher.add_coordinate(37.8383, -122.4167, 'SF-North')
        self.geohasher.add_coordinate(37.7333, -122.4167, 'SF-South')


    def tearDown(self):
        self.geohasher.remove_coordinate('SF')
        self.geohasher.remove_coordinate('SF-West')
        self.geohasher.remove_coordinate('SF-East')
        self.geohasher.remove_coordinate('SF-North')
        self.geohasher.remove_coordinate('SF-South')
        

    def test_haversine(self):
        self.assertTrue(self.geohasher.haversine(37.7833, -122.4167, 37.7833, -122.4167) < 5000)
        self.assertTrue(self.geohasher.haversine(37.7833, -122.4167, 37.7833, -122.4667) < 5000)
        self.assertTrue(self.geohasher.haversine(37.7833, -122.4167, 37.7833, -122.3667) < 5000)
        self.assertFalse(self.geohasher.haversine(37.7833, -122.4167, 37.8383, -122.3667) < 5000)
        self.assertFalse(self.geohasher.haversine(37.7833, -122.4167, 37.7333, -122.3667) < 5000)


    def test_query_by_radius(self):
        result = self.geohasher.query_by_radius(37.7833, -122.4167, 5000)
        values = [r['key'] for r in result]

        self.assertEqual(len(result), 3)
        self.assertItemsEqual(values, ['SF', 'SF-West', 'SF-East'])

        result = self.geohasher.query_by_radius(37.7833, -122.4167, 100)
        values = [r['key'] for r in result]

        self.assertEqual(len(result), 1)
        self.assertItemsEqual(values, ['SF'])

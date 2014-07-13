#!/usr/bin/env python 

import unittest
from .. import encode


class EncodeTestCase(unittest.TestCase):

    def test_encode_int(self):
        self.assertEqual(encode.encode_int(0, 0, steps=1), 3)
        self.assertEqual(encode.encode_int(0, 0, steps=2), 12)

        self.assertEqual(encode.encode_int(90, 0, steps=2), 14)
        self.assertEqual(encode.encode_int(-90, 0, steps=2), 4)

        self.assertEqual(encode.encode_int(90, 180, steps=2), 15)
        self.assertEqual(encode.encode_int(90, -180, steps=2), 10)

        self.assertEqual(encode.encode_int(-90, -180, steps=2), 0)

        self.assertEqual(encode.encode_int(-90, -180), 0)
        self.assertEqual(encode.encode_int(90, 180), 18446744073709551615L)

    def test_decode_int(self):
        self.assertEqual(encode.decode_int(3, steps=2), (-22.5, -45.0, 22.5, 45.0))
        
        lat, lon, lat_err, lon_err = encode.decode_int(0)
        self.assertEqual((round(lat), round(lon)), (-90, -180))

        lat, lon, lat_err, lon_err = encode.decode_int(18446744073709551615L)
        self.assertEqual((round(lat), round(lon)), (90, 180))

    def test_get_neighbor_int(self):
        self.assertEqual(encode.get_neighbor_int(3, steps=2), [6, 2, 1, 9, 4, 12, 0, 8]) 

    def test_move_lat(self):
        self.assertEqual(encode.move_lat(3, steps=2, flag=1), 9) 
        self.assertEqual(encode.move_lat(3, steps=2, flag=-1), 1) 

    def test_move_lon(self):
        self.assertEqual(encode.move_lon(3, steps=2, flag=1), 6) 
        self.assertEqual(encode.move_lon(3, steps=2, flag=-1), 2) 

    def test_to_float(self):
        self.assertTrue(0 == encode.to_float(''))
        self.assertTrue(1.0 == encode.to_float('1'))
        self.assertTrue(1.2 == encode.to_float('1.2'))
        self.assertTrue(1.0 == encode.to_float(1))
        self.assertTrue(1.0 == encode.to_float(1.0))
        self.assertTrue(0 == encode.to_float('TEST'))

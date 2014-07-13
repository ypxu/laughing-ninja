#!/usr/bin/env python

import encode
from math import radians, cos, sin, asin, sqrt


# resolution in meters
RANGE_INDEX = [0.6,            # 52
               1,              # 50
               2.19,           # 48
               4.57,           # 46
               9.34,           # 44
               14.4,           # 42
               33.18,          # 40
               62.1,           # 38
               128.55,         # 36
               252.9,          # 34
               510.02,         # 32
               1015.8,         # 30
               2236.5,         # 28
               3866.9,         # 26
               8749.7,         # 24
               15664,          # 22
               33163.5,        # 20
               72226.3,        # 18
               150350,         # 16
               306600,         # 14
               474640,         # 12
               1099600,        # 10
               2349600,        # 8
               4849600,        # 6
               10018863        # 4
               ]


class GeoHasher(object):

    def __init__(self, redis_client, lookup_key='geo', resolution=64):
        self.redis_client = redis_client
        self.resolution = resolution
        self.steps = resolution / 2
        self.lookup_key = lookup_key

    def add_coordinate(self, lat, lon, value):
        hash_val = encode.encode_int(lat, lon, steps=self.steps)
        self.redis_client.zadd(self.lookup_key, value, hash_val)

    def remove_coordinate(self, value):
        self.redis_client.zrem(self.lookup_key, value)

    def query_by_radius(self, lat, lon, radius):
        '''
        Query points within certain radius around point (lat/lon)
        '''

        lat = encode.to_float(lat)
        lon = encode.to_float(lon)
        radius = encode.to_float(radius)

        resolution = self.radius_to_range(radius)
        hash_val = encode.encode_int(lat, lon, steps=resolution / 2)
        neighbors = encode.get_neighbor_int(hash_val, steps=resolution / 2)
        shift_bits = self.resolution - resolution

        points = [hash_val] + neighbors
        ranges = []
        for p in points:
            min_p = self.left_shift(p, shift_bits)
            max_p = self.left_shift(p + 1, shift_bits)
            ranges.append((min_p, max_p))

        pipe = self.redis_client.pipeline()
        for min_r, max_r in ranges:
            pipe.zrangebyscore(self.lookup_key, min_r, max_r, withscores=True)
        responses = pipe.execute()

        results = []
        for resp in responses:
            if not len(resp) > 0:
                continue
            for key, score in resp:
                lat_r, lon_r, _, _ = encode.decode_int(score,
                                                       steps=self.steps)
                dist = self.haversine(lat, lon, lat_r, lon_r)
                if dist <= radius:
                    results.append({'key': key, 'lat': lat_r,
                                    'lon': lon_r, 'dist': dist})
        return results

    def haversine(self, lat1, lon1, lat2, lon2):
        '''
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)

        http://stackoverflow.com/a/4913653

        '''
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        # 6367 km is the radius of the Earth
        meters = 6367 * 1000 * c
        return meters

    def radius_to_range(self, radius):
        '''
        https://github.com/yinqiwen/ardb/blob/master/doc/spatial-index.md
        '''
        for key, val in enumerate(RANGE_INDEX):
            if (radius - val) < (RANGE_INDEX[key+1] - radius):
                return 52 - key * 2
        return 2

    def left_shift(self, val, shift):
        return val << shift

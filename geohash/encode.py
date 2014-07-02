#!/usr/bin/env python

from __future__ import division


def encode_int(lat, lon, lat_max=90, lat_min=-90,
               lon_max=180, lon_min=-180, steps=32):
    if isinstance(lat, basestring):
        lat = float(lat)
    if isinstance(lon, basestring):
        lon = float(lon)
    if (steps > 32 or lat < lat_min or lat > lat_max or
        lon < lon_min or lon > lon_max):
        return None

    bit_arr = []
    for i in xrange(steps):
        if lat_max - lat > lat - lat_min:
            lat_bit = '0'
            lat_max = (lat_max + lat_min) / 2
        else:
            lat_bit = '1'
            lat_min = (lat_max + lat_min) / 2
        if lon_max - lon > lon - lon_min:
            lon_bit = '0'
            lon_max = (lon_max + lon_min) / 2
        else:
            lon_bit = '1'
            lon_min = (lon_max + lon_min) / 2
        bit_arr.append(lat_bit)
        bit_arr.append(lon_bit)
    return int(''.join(bit_arr), 2)


def decode_int(value, lat_max=90, lat_min=-90,
               lon_max=180, lon_min=-180, steps=32):
    bit_arr = bin(int(value))[2:].zfill(steps*2)
    lat_lon = [lat_min, lat_max, lon_min, lon_max]
    LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = 0, 1, 2, 3
    for i in xrange(steps):
        lat_bit = bit_arr[i*2]
        lon_bit = bit_arr[i*2 + 1]
        if lat_bit == '1':
            lat_lon[LAT_MIN] = (lat_lon[LAT_MIN] + lat_lon[LAT_MAX]) / 2
        elif lat_bit == '0':
            lat_lon[LAT_MAX] = (lat_lon[LAT_MIN] + lat_lon[LAT_MAX]) / 2
        if lon_bit == '1':
            lat_lon[LON_MIN] = (lat_lon[LON_MIN] + lat_lon[LON_MAX]) / 2
        elif lon_bit == '0':
            lat_lon[LON_MAX] = (lat_lon[LON_MIN] + lat_lon[LON_MAX]) / 2
    lat = (lat_lon[LAT_MIN] + lat_lon[LAT_MAX]) / 2
    lon = (lat_lon[LON_MIN] + lat_lon[LON_MAX]) / 2
    return lat, lon, lat_lon[LAT_MAX] - lat, lat_lon[LON_MAX] - lon


def get_neighbor_int(val, steps=32):
    # North
    north = move_lat(val, steps, 0)
    north = move_lon(north, steps, 1)
    # South
    south = move_lat(val, steps, 0)
    south = move_lon(south, steps, -1)
    # West
    west = move_lat(val, steps, -1)
    west = move_lon(west, steps, 0)
    # East
    east = move_lat(val, steps, 1)
    east = move_lon(east, steps, 0)
    # North West
    north_west = move_lat(val, steps, -1)
    north_west = move_lon(north_west, steps, 1)
    # North East
    north_east = move_lat(val, steps, 1)
    north_east = move_lon(north_east, steps, 1)
    # South West
    south_west = move_lat(val, steps, -1)
    south_west = move_lon(south_west, steps, -1)
    # South East
    south_east = move_lat(val, steps, 1)
    south_east = move_lon(south_east, steps, -1)
    return [north, south, west, east,
        north_west, north_east, south_west, south_east]


def move_lat(val, steps, flag):
    bit_len = steps * 2
    lat_val = val & int('aaaaaaaaaaaaaaaa', 16)
    lon_val = val & int('5555555555555555', 16)
    step_val = int('5555555555555555', 16) >> (64 - bit_len)
    if flag > 0:
        lat_val += (step_val + 1)
    elif flag < 0:
        lat_val |= step_val
        lat_val -= (step_val + 1)
    lat_val &= int('aaaaaaaaaaaaaaaa', 16) >> (64 - bit_len)
    return lat_val | lon_val


def move_lon(val, steps, flag):
    bit_len = steps * 2
    lat_val = val & int('aaaaaaaaaaaaaaaa', 16)
    lon_val = val & int('5555555555555555', 16)
    step_val = int('aaaaaaaaaaaaaaaa', 16) >> (64 - bit_len)
    if flag > 0:
        lon_val += (step_val + 1)
    elif flag < 0:
        lon_val |= step_val
        lon_val -= (step_val + 1)
    lon_val &= int('5555555555555555', 16) >> (64 - bit_len)
    return lat_val | lon_val

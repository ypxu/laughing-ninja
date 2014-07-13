#!/usr/bin/env python

from __future__ import division
import logging

logger = logging.getLogger()


def encode_int(lat, lon, lat_max=90, lat_min=-90,
               lon_max=180, lon_min=-180, steps=32):
    '''
    Encode the latitude/longitude into integer based on resolutions
    '''
    lat = to_float(lat)
    lon = to_float(lon)
    if steps <= 32 and lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
        bit_arr = []
        for i in xrange(steps):
            # latitude
            if lat_max - lat > lat - lat_min:
                lat_bit = '0'
                lat_max = (lat_max + lat_min) / 2
            else:
                lat_bit = '1'
                lat_min = (lat_max + lat_min) / 2
            # longitude
            if lon_max - lon > lon - lon_min:
                lon_bit = '0'
                lon_max = (lon_max + lon_min) / 2
            else:
                lon_bit = '1'
                lon_min = (lon_max + lon_min) / 2
            # append latitude bit and longitude bit into bit array
            bit_arr.append(lat_bit)
            bit_arr.append(lon_bit)
        # convert bit_arr to corresponding integer
        return int(''.join(bit_arr), 2)


def decode_int(value, lat_max=90, lat_min=-90,
               lon_max=180, lon_min=-180, steps=32):
    '''
    Reverse of encode_int
    '''
    # convert integer to corresponding bit array.
    bit_arr = bin(int(value))[2:].zfill(steps*2)
    # init result for latitude and longitude
    lat_lon = [lat_min, lat_max, lon_min, lon_max]
    LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = 0, 1, 2, 3

    for i in xrange(steps):
        lat_bit = bit_arr[i*2]
        lon_bit = bit_arr[i*2 + 1]
        # latitude
        if lat_bit == '1':
            lat_lon[LAT_MIN] = (lat_lon[LAT_MIN] + lat_lon[LAT_MAX]) / 2
        elif lat_bit == '0':
            lat_lon[LAT_MAX] = (lat_lon[LAT_MIN] + lat_lon[LAT_MAX]) / 2
        # longitude
        if lon_bit == '1':
            lat_lon[LON_MIN] = (lat_lon[LON_MIN] + lat_lon[LON_MAX]) / 2
        elif lon_bit == '0':
            lat_lon[LON_MAX] = (lat_lon[LON_MIN] + lat_lon[LON_MAX]) / 2
    # average latitude and longitude
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
    '''
    Move latitude to different direction based on flag
    '''
    bit_len = steps * 2
    lat_val = val & int('aaaaaaaaaaaaaaaa', 16)
    lon_val = val & int('5555555555555555', 16)
    step_val = int('5555555555555555', 16) >> (64 - bit_len)
    # East
    if flag > 0:
        lat_val += (step_val + 1)
    # West
    elif flag < 0:
        lat_val |= step_val
        lat_val -= (step_val + 1)
    # Reset carryover bits for longitude
    lat_val &= int('aaaaaaaaaaaaaaaa', 16) >> (64 - bit_len)
    return lat_val | lon_val


def move_lon(val, steps, flag):
    '''
    Move longitude to different direction based on flag
    '''
    bit_len = steps * 2
    lat_val = val & int('aaaaaaaaaaaaaaaa', 16)
    lon_val = val & int('5555555555555555', 16)
    step_val = int('aaaaaaaaaaaaaaaa', 16) >> (64 - bit_len)
    # North
    if flag > 0:
        lon_val += (step_val + 1)
    # South
    elif flag < 0:
        lon_val |= step_val
        lon_val -= (step_val + 1)
    # Reset carryover bits for latitude
    lon_val &= int('5555555555555555', 16) >> (64 - bit_len)
    return lat_val | lon_val


def to_float(val):
    try:
        return float(val)
    except:
        logger.error('Bad float value {0}'.format(val))
        return 0

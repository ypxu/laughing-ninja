#!/usr/bin/env python

import requests
from xml.etree import ElementTree as ET


class Base(object):
    pass


class Agency(Base):

    def __init__(self, **kwargs):
        self.title = kwargs.get('title', '')
        self.regionTitle = kwargs.get('regionTitle', '')
        self.tag = kwargs.get('tag', '')


class Route(Base):

    def __init__(self, **kwargs):
        self.tag = kwargs.get('tag', '')
        self.title = kwargs.get('title', '')
        self.shortTitle = kwargs.get('shortTitle', '')
        self.color = kwargs.get('color', '')
        self.oppositeColor = kwargs.get('oppositeColor', '')
        self.latMin = kwargs.get('latMin', '')
        self.latMax = kwargs.get('latMax', '')
        self.lonMin = kwargs.get('lonMin', '')
        self.lonMax = kwargs.get('lonMax', '')


class RouteConfig(Base):

    def __init__(self, **kwargs):
        self.tag = kwargs.get('tag', '')
        self.title = kwargs.get('title', '')
        self.shortTitle = kwargs.get('shortTitle', '')
        self.color = kwargs.get('color', '')
        self.oppositeColor = kwargs.get('oppositeColor', '')
        self.latMin = kwargs.get('latMin', '')
        self.latMax = kwargs.get('latMax', '')
        self.lonMin = kwargs.get('lonMin', '')
        self.lonMax = kwargs.get('lonMax', '')
        self.stops = kwargs.get('stops', [])
        self.paths = kwargs.get('paths', [])
        self.directions = kwargs.get('directions', [])


class Stop(Base):

    def __init__(self, **kwargs):
        self.tag = kwargs.get('tag', '')
        self.title = kwargs.get('title', '')
        self.shortTitle = kwargs.get('shortTitle', '')
        self.lat = kwargs.get('lat', '')
        self.lon = kwargs.get('lon', '')
        self.stopId = kwargs.get('stopId', '')


class Direction(Base):

    def __init__(self, **kwargs):
        self.tag = kwargs.get('tag', '')
        self.title = kwargs.get('title', '')
        self.name = kwargs.get('name', '')
        self.stops = kwargs.get('stops', [])
        self.predictions = kwargs.get('predictions', [])


class Point(Base):

    def __init__(self, **kwargs):
        self.lat = kwargs.get('lat', '')
        self.lon = kwargs.get('lon', '')


class Path(Base):

    def __init__(self, **kwargs):
        self.points = kwargs.get('points', [])


class Predictions(Base):

    def __init__(self, **kwargs):
        self.agencyTitle = kwargs.get('agencyTitle', '')
        self.routeTitle = kwargs.get('routeTitle', '')
        self.routeTag = kwargs.get('routeTag', '')
        self.stopTitle = kwargs.get('stopTitle', '')
        self.stopTag = kwargs.get('stopTag', '')
        self.directions = kwargs.get('directions', [])


class Prediction(Base):

    def __init__(self, **kwargs):
        self.epochTime = kwargs.get('epochTime', '')
        self.seconds = kwargs.get('seconds', '')
        self.minutes = kwargs.get('minutes', '')
        self.isDeparture = kwargs.get('isDeparture', '')
        self.affectedByLayover = kwargs.get('affectedByLayover', '')
        self.dirTag = kwargs.get('dirTag', '')
        self.vehicle = kwargs.get('vehicle', '')
        self.vehiclesInConsist = kwargs.get('vehiclesInConsist', '')
        self.block = kwargs.get('block', '')
        self.tripTag = kwargs.get('tripTag', '')


class Vehicle(Base):

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', '')


class Command(object):

    api_base = 'http://webservices.nextbus.com/service/publicXMLFeed\
?command={command}&'

    def make_request(self, cmd, params={}):

        url = self.api_base.format(command=cmd) + '&'.join(
            [str(k) + '=' + str(v) for k, v in params.iteritems()])

        response = requests.get(url)
        if not response.status_code == 200:
            return []
        else:
            return ET.fromstring(response.text)

    def get_agency_list(self):
        agency_list = []
        response = self.make_request('agencyList')
        for child in response:
            agency_list.append(Agency(**child.attrib))
        return agency_list

    def get_route_list(self, agency_tag):
        route_list = []
        response = self.make_request('routeList', {'a': agency_tag or ''})
        for child in response:
            route_list.append(Route(**child.attrib))
        return route_list

    def get_route_config(self, agency_tag, route_tag=''):
        params = {'a': agency_tag or ''}
        if route_tag:
            params['r'] = route_tag
        response = self.make_request('routeConfig', params)

        route_list = []
        for route in response:
            route_config = RouteConfig(**route.attrib)
            for child in route:
                if child.tag == 'stop':
                    route_config.stops.append(Stop(**child.attrib))
                elif child.tag == 'direction':
                    sub_stop_list = []
                    for sub_child in child:
                        sub_stop_list.append(Stop(**sub_child.attrib))
                    direction = Direction(**child.attrib)
                    direction.stops = sub_stop_list
                    route_config.directions.append(direction)
                elif child.tag == 'path':
                    point_list = []
                    for point in child:
                        point_list.append(Point(**point.attrib))
                    route_config.paths.append(Path(points=point_list))
            route_list.append(route_config)
        return route_list

    def get_predictions_by_stopId(self, agency_tag, stop_id, route_tag=''):
        params = {'a': agency_tag or '', 'stopId': stop_id or ''}
        if route_tag:
            params['routeTag'] = route_tag
        response = self.make_request('predictions', params)
        prediction_list = []
        for predictions in response:
            direction_list = []
            for direction in predictions:
                prediction_list = []
                for prediction in direction:
                    prediction_list.append(Prediction(**prediction.attrib))
                direction_list.append(
                    Direction(predictions=prediction_list, **direction.attrib))
            prediction_list.append(
                Predictions(directions=direction_list, **predictions.attrib))
        return prediction_list

    def get_predictions_by_stopTag(self, agency_tag, stopTag, route_tag):
        response = self.make_request('predictions', {'a': agency_tag,
                                     's': stopTag, 'r': route_tag})
        prediction_list = []
        for resp in response:
            predictions = Predictions(**resp.attrib)
            for child in resp:
                # We skip non-direction node
                if not child.attrib.get('title'):
                    continue
                direction = Direction(**child.attrib)
                for sub_child in child:
                    direction.predictions.append(
                        Prediction(**sub_child.attrib))
                predictions.directions.append(direction)
            prediction_list.append(predictions)
        return prediction_list

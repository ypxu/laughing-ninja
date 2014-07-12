#!/usr/bin/env python

import argparse
import json
import flask
import thread
import geohash
import logging
from geohash import GeoHasher
from redis import Redis
from nextbus import nextbus
from flask import Flask, Response
from flask import request, render_template, send_from_directory
from monkey_patch_flask import patch_flask_jsonify, CustomEncoder


app = Flask(__name__, template_folder='')
app.config.from_pyfile('config/config.cfg')

cmd = nextbus.Command()
client = Redis()
geo_cli = GeoHasher(redis_client=client, lookup_key='stops')


def init_redis():
    app.logger.debug('Initialize redis from nextbus.')
    agency_list = cmd.get_agency_list()
    app.logger.debug('### Add %s agency' % len(agency_list))

    agency_key = 'agency'
    for agency in agency_list:
        if not agency or client.sismember(agency_key, agency.tag):
            continue
        routes = cmd.get_route_config(agency.tag)
        app.logger.debug('### Add %s agency, %s routes' % (
            agency.tag, len(routes)))
        for route in routes:
            init_route(agency, route)
        client.set('%s:%s' % (agency_key, agency.tag), json.dumps(
            agency, cls=CustomEncoder))
        client.sadd(agency_key, agency.tag)
    app.logger.debug('Done initialization redis.')


def init_route(agency, route, route_key='route', stop_key='stop'):
    if not route or client.sismember(route_key, route.tag):
        return
    stops = route.stops
    app.logger.debug('### Add %s agency, %s routes, %s stops' % (
        agency.tag, route.tag, len(stops)))
    for stop in stops:
        stop_k = '%s:%s:%s:%s' % (stop_key, agency.tag, route.tag, stop.tag)
        client.sadd(stop_k, stop.tag)
        client.set(stop_k, json.dumps(stop, cls=CustomEncoder))
        geo_cli.add_coordinate(stop.lat, stop.lon, stop_k)
    client.set('%s:%s:%s' % (route_key, agency.tag, route.tag),
        json.dumps(route, cls=CustomEncoder))
    client.sadd(route_key, route.tag)


def setup_logging():
    app.logger.addHandler(logging.StreamHandler())
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/agency.json")
def agency():
    data = cmd.get_agency_list()
    return flask.jsonify(result=data)


@app.route("/api/route.json")
def route():
    agency = request.args.get('agency')
    data = cmd.get_route_list(agency)
    return flask.jsonify(result=data)


@app.route("/api/route_config.json")
def route_config():
    agency, route = (request.args.get('agency'),
        request.args.get('route'))
    data = cmd.get_route_config(agency, route)
    return flask.jsonify(result=data)


@app.route("/api/stop_config.json")
def stop_config():
    stop = {}
    stop_key = request.args.get("stop", '')
    if stop_key.startswith('stop'):
        stop = json.loads(client.get(stop_key) or {})
        _, agency_tag, route_tag, stop_tag = stop_key.split(':')
        predictions = cmd.get_predictions_by_stopTag(agency_tag,
            stop_tag, route_tag)
        if len(predictions) > 0:
            stop['agencyTitle'] = predictions[0].agencyTitle
            stop['routeTitle'] = predictions[0].routeTitle
            stop['stopTitle'] = predictions[0].stopTitle

            for prediction in predictions:
                for direction in prediction.directions:
                    if len(direction.predictions) > 0:
                        stop['prediction'] = direction.predictions[0]
                        stop['direction'] = direction.title
                        break

    return flask.jsonify(result=stop)


@app.route("/api/near_routes.json")
def near_routes():
    lat, lon, rad = (request.args.get('lat', ''),
        request.args.get('lon', ''), request.args.get('radius', ''))
    return flask.jsonify(result=geo_cli.query_by_radius(lat, lon, rad))


@app.route("/js/<filename>")
def js(filename):
    return send_from_directory('js', filename)


@app.route("/css/<filename>")
def css(filename):
    return send_from_directory('css', filename)


if __name__ == '__main__':
    # Development

    parser = argparse.ArgumentParser(description='Run transit app')
    parser.add_argument('--debug', action='store_true',
      help="debug mode", required=False)
    parser.add_argument('--host', action='store',
      help="host", required=False, default='0.0.0.0')
    parser.add_argument('--port', action='store', type=int,
      help="port", required=False, default=5000)

    options = parser.parse_args()

    thread.start_new_thread(init_redis, ())

    patch_flask_jsonify()

    setup_logging()

    app.run(host=options.host, port=options.port,
      debug=options.debug)

else:
    # Deploy with Gunicorn (Production)

    from werkzeug.contrib.fixers import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app)

    thread.start_new_thread(init_redis, ())

    patch_flask_jsonify()

    setup_logging()

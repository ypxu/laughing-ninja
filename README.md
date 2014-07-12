Realtime Transit Map (Departure Times)
==============

This project intends as demo/prototype of geo hashing. It provides geolocated departure timetable for user in realtime. Based on user current latitude and longitude, it lists out nearby public transportation stops within certain radius.

The underlying technique is based on geo hashing to find the nearest stops. The latitude and longitude of all stops are converted to 64bit integer and stored in redis's sorted set. When searching nearby stops around user, we will convert the latitude and longitude to corresponding 64bit integer based on desired resolution.

The departure times will be fetched after we find out the nearby stops.

[Demo](http://demo.trenvenue.com) (Linode1024)

# Platform
* Python
  * Use Python extensively on work or side-project for last few years.
  * Could use Java, Go or Ruby to rewrite the whole backend. For fun!

# Back-end
* Flask
  * First time use Flask as main framework, besides toy projects
  * Flask is easy to customize. It fits very well for this type of project.
* Redis
  * Most recently used No-SQL database. Have used it for last two years.
  * Very fast database with data structure build-in, such as sorted set.
  * Keyspace notification (v2.8 up) and Lua support. :)

# Front-end
* jQuery
  * Use it for last few years, since v1.4
* Backbone
  * Most familiar javascript framework, use it since early 2012
  * Rewrite a existed Flex-based application to backbone-based js application

# Deployment
* Gunicorn
  * Easy to use pre-fork WSGI Http Server
  * First time use it. Similar to thin in Ruby on Rail
* Supervisord
  * Manage spawn preocess
* Capistrano
  * Manage production deployment, Have used it for a few projects.
  * Want to try Fabric. more pythonic way

# Future Improvement
* Add unittest for nextbus module
* Add unittest for Flask's request handler
* Enhance UI with websocket to show departure time
* Show all stops's departure time of a route
* Cache prediction response to improve performance using redis. (ttl < 1 min)

# Reference
* [Geohash](http://en.wikipedia.org/wiki/Geohash)
* [Spatial Index in yinqiwen/ardb](https://github.com/yinqiwen/ardb/blob/master/doc/spatial-index.md)
* [Geohashing](http://xkcd.com/426/)

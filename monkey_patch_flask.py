#!/usr/bin/env python

import json
from nextbus import nextbus


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, nextbus.Base):
	    return obj.__dict__
	return super(CustomEncoder, self).default(obj) 

def patch_flask_jsonify():
    '''Patch flask jsonify to provide encoder for nextbus class'''

    import flask
    from json import dumps
    from flask import current_app, request

    def jsonify(*args, **kwargs):
        indent = None
        if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] \
            and not request.is_xhr:
            indent = 2
        return current_app.response_class(dumps(dict(*args, **kwargs),
            indent=indent, cls=CustomEncoder),
            mimetype='application/json')
    flask.jsonify = jsonify

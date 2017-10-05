#!/usr/bin/env python

import webapp2
import config
from codes.controllers.view.StreamViewController import StreamViewController
from codes.controllers.view.PhotoViewController import PhotoViewController

from codes.controllers.api.StreamAPIController import StreamAPIController

StreamViewController.JINJA_ENVIRONMENT = config.JINJA_ENVIRONMENT
StreamAPIController.JINJA_ENVIRONMENT = config.JINJA_ENVIRONMENT

app = webapp2.WSGIApplication([
    webapp2.Route('/api/create_stream', StreamAPIController, handler_method='create',\
        methods=['POST']),
    webapp2.Route('/api/management_data', StreamAPIController, handler_method='management',\
        methods=['POST']),
    webapp2.Route('/api/view', StreamAPIController, handler_method='view',\
        methods=['POST']),
    webapp2.Route('/api/all_streams', StreamAPIController, handler_method='all_streams',\
        methods=['POST']),
    webapp2.Route('/api/login', StreamAPIController, handler_method='login',\
        methods=['GET'])
], debug=config.debug)

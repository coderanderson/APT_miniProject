#!/usr/bin/env python

import webapp2
import config
from codes.controllers.StreamController import StreamController
from codes.controllers.PhotoController import PhotoController

StreamController.JINJA_ENVIRONMENT = config.JINJA_ENVIRONMENT
PhotoController.JINJA_ENVIRONMENT = config.JINJA_ENVIRONMENT

app = webapp2.WSGIApplication([
    webapp2.Route('/view_stream', StreamController, handler_method='view',\
        methods=['GET']),
    webapp2.Route('/create_stream', StreamController, handler_method='create',\
        methods=['POST']),
    webapp2.Route('/', StreamController, handler_method='show_create_menu',\
        methods=['GET']),
    webapp2.Route('/invite', StreamController, handler_method='invite',\
        methods=['GET']),

    webapp2.Route('/upload_photo', PhotoController, handler_method='show_upload_menu',\
        methods=['GET']),
    webapp2.Route('/send_photo', PhotoController, handler_method='create',\
        methods=['POST']),
    webapp2.Route('/photo_img', PhotoController, handler_method='view', methods=['GET']),
], debug=config.debug)

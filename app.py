#!/usr/bin/env python

import webapp2
import config
from codes.controllers.view.StreamViewController import StreamViewController
from codes.controllers.view.PhotoViewController import PhotoViewController
from codes.controllers.view.UserViewController import UserViewController

from codes.controllers.api.StreamAPIController import StreamAPIController
from codes.controllers.api.PhotoAPIController import PhotoAPIController

StreamViewController.JINJA_ENVIRONMENT = config.JINJA_ENVIRONMENT
PhotoViewController.JINJA_ENVIRONMENT = config.JINJA_ENVIRONMENT
UserViewController.JINJA_ENVIRONMENT = config.JINJA_ENVIRONMENT

app = webapp2.WSGIApplication([
    webapp2.Route('/api/create_stream', StreamAPIController, handler_method='create',
                  methods=['POST']),
    webapp2.Route('/api/management_data', StreamAPIController, handler_method='management',
                  methods=['POST']),
    webapp2.Route('/api/view', StreamAPIController, handler_method='view',
                  methods=['POST']),
    webapp2.Route('/api/all_streams', StreamAPIController, handler_method='all_streams',
                  methods=['POST']),
    webapp2.Route('/api/trending_streams', StreamAPIController,
                  handler_method='trending_streams', methods=['POST']),
    webapp2.Route('/api/unsubscribe_streams', StreamAPIController,
                  handler_method='unsubscribe_selected_streams', methods=['POST']),
    webapp2.Route('/api/delete_streams', StreamAPIController,
                  handler_method='delete_selected_streams', methods=['POST']),
    webapp2.Route('/api/run_cron', StreamAPIController,
                  handler_method='run_cron', methods=['POST', 'GET']),
    webapp2.Route('/api/cron_trending_streams', StreamAPIController,
                  handler_method='cron_trending_streams', methods=['POST', 'GET']),
    webapp2.Route('/api/upload_photo', PhotoAPIController, handler_method='create',
                  methods=['POST']),
    webapp2.Route('/manage', StreamViewController, handler_method='show_manage_menu',
                  methods=['GET']),
    webapp2.Route('/create_stream', StreamViewController, handler_method='create',
                  methods=['POST']),
    webapp2.Route('/create_stream_menu', StreamViewController, handler_method='show_create_menu',
                  methods=['GET']),
    webapp2.Route('/trending', StreamViewController, handler_method='show_trending_streams',
                  methods=['GET']),
    webapp2.Route('/view_stream', StreamViewController, handler_method='view',
                  methods=['GET']),
    webapp2.Route('/view_all', StreamViewController, handler_method='all_streams',
                  methods=['GET']),
    webapp2.Route('/invite', StreamViewController, handler_method='invite',
                  methods=['GET']),
    webapp2.Route('/search', StreamViewController, handler_method='search_stream',
                  methods=['GET']),

    webapp2.Route('/search_suggest', StreamViewController, handler_method='search_suggest',
                  methods=['GET']),

    webapp2.Route('/update_trending_info', StreamViewController, handler_method='update_trending_info',
                  methods=['GET']),
    webapp2.Route('/get_photo', PhotoViewController, handler_method='view',
                  methods=['GET']),
    webapp2.Route('/send_photo', PhotoViewController, handler_method='create',
                  methods=['POST']),
    webapp2.Route('/login', UserViewController, handler_method='front_page',
                  methods=['GET']),
    webapp2.Route('/', UserViewController, handler_method='front_page',
                  methods=['GET']),
], debug=config.debug)

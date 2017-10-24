import webapp2
import urllib
import urllib2
import datetime
import json

import codes
from codes.models import *

from google.appengine.ext import ndb
from google.appengine.api import users as gusers
from google.appengine.api import mail
from google.appengine.api import urlfetch

from codes.controllers.view.UserViewController import UserViewController

class StreamAPIController(webapp2.RequestHandler):

    def create(self, from_view=False):
        self.response.headers['Content-Type'] = 'application/json'
        if gusers.get_current_user():
            stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
            cover_url = self.request.get('cover_url', '')
            message = self.request.get('message', '')
            invitee_emails = self.request.get('invitee_emails', '')
            invitee_emails = [ e.strip() for e in invitee_emails.split(',') if e.strip()!='' ]
            tags = self.request.get('tags', '')

            create_result = Stream.create(stream_name, gusers.get_current_user().email(), cover_url,\
                    message, invitee_emails, self.request.host_url, tags)

            if 'error' in create_result:
                result = {'error': create_result['error']}
                self.response.set_status(409)
                self.response.out.write(json.dumps(result))
            else:
                self.response.set_status(200)
                self.response.out.write(json.dumps({}))
        else:
            self.response.set_status(403)
            self.response.out.write(json.dumps({'error': UserViewController.login_error}))

    def view(self):
        self.response.headers['Content-Type'] = 'application/json'

        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        page = int(self.request.get('page', 1))
        per_page = int(self.request.get('per_page', 10))

        result = Stream.view(stream_name, page, per_page)
        if result:
            self.response.set_status(200)
            self.response.out.write(json.dumps(result,\
                default = lambda d: d.isoformat() if hasattr(d, 'isoformat') else d ))
        else:
            self.error(404)

    def all_streams_matching(self):
        self.response.headers['Content-Type'] = 'application/json'
        query = self.request.get('query', '')
        result = Stream.all_streams_matching(query)
        self.response.out.write(json.dumps(result))
        if len(result) is 0:
            self.response.set_status(204)
        else:
            self.response.set_status(200)

    def trending_streams(self):
        self.response.headers['Content-Type'] = 'application/json'
        duration = int(self.request.get('duration', 60*60))
        result = Stream.get_top_trending_streams_now(duration)
        self.response.out.write(json.dumps(result))
        self.response.set_status(200)

    def run_cron(self):
        some_url = self.request.host_url + '/api/cron_trending_streams'
        content = urllib2.urlopen(some_url).read()
        self.response.set_status(200)

    def cron_trending_streams(self):
        Stream.generate_trending_report(self.request.host_url,\
                codes.controllers.view.StreamViewController.StreamViewController.view_route)
        self.response.set_status(200)

    def management(self):
        self.response.headers['Content-Type'] = 'application/json'
        if gusers.get_current_user():
            result = Stream.get_related_streams_of_user(gusers.get_current_user().email())
            self.response.set_status(200)
            self.response.out.write(json.dumps(result))
        else:
            self.response.set_status(403)
            self.response.out.write(json.dumps({ 'error': UserViewController.login_error }))

    def delete_selected_streams(self):
        remove_list = self.request.get('streams').split(',')
        self.make_management_changes(remove_list, [])

    def unsubscribe_selected_streams(self):
        unsubscribe_list = self.request.get('streams').split(',')
        self.make_management_changes([], unsubscribe_list)

    def make_management_changes(self, remove_list, unsubscribe_list):
        self.response.headers['Content-Type'] = 'application/json'
        if gusers.get_current_user():
            user_email = gusers.get_current_user().email()
            Stream.bulk_remove_unsubscribe(remove_list, unsubscribe_list, user_email)
            self.response.set_status(200)
        else:
            self.response.set_status(403)
            self.response.out.write(json.dumps({'error': UserViewController.login_error}))

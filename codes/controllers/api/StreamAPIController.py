import webapp2
import urllib
import time
import datetime
import json
import math
import operator

import codes
from codes.models import *

from google.appengine.ext import ndb
from google.appengine.api import users as gusers
from google.appengine.api import mail

STREAM_INDEX = 'stream_index'

class StreamAPIController(webapp2.RequestHandler):

    def create(self, from_view=False):
        if gusers.get_current_user():
            stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
            cover_url = self.request.get('cover_url', '')
            message = self.request.get('message', '')
            invitee_emails = self.request.get('invitee_emails', '')
            stream = Stream.query().filter(Stream.name == stream_name).get()

            if stream:
                result={ 'error': 'duplicate stream name' }
                if not from_view:
                    self.response.set_status(409)
                    self.response.out.write(json.dumps(result))
                else:
                    return result
            else:
                user = User.query().filter(User.email == gusers.get_current_user().email()).get()
                stream = Stream()
                if cover_url:
                    stream.cover_url = cover_url
                stream.name = stream_name
                stream.tags = self.request.get('tags', '')
                stream.owner = user.key
                stream.put()
                user.subscription_list.append(stream.key)
                user.put()
                stream.owner = user.key
                stream.put()

                invitee_emails = [ e.strip() for e in invitee_emails.split(',') if e.strip()!='' ]
                invitation_link = self.request.host_url + '/invite?stream_name=' + stream_name
                email_body = codes.controllers.view.StreamViewController.\
                        StreamViewController.JINJA_ENVIRONMENT.get_template('invitation.html')
                email_body = email_body.render({'invitation_link': invitation_link,\
                    'message': message, 'stream_name': stream_name})

                for e in invitee_emails:
                    mail.send_mail(sender=gusers.get_current_user().email(), to=e,\
                        subject="Stream Invitation",body='', html=email_body)

                if not from_view:
                    self.response.set_status(200)
                else:
                    return None
        else:
            if not from_view:
                self.error(403)
            else:
                return {'error': 'you should login first'}

    def view(self):
        self.response.headers['Content-Type'] = 'application/json'

        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        page = int(self.request.get('page', 1))
        per_page = int(self.request.get('per_page', 10))

        stream = Stream.query().filter(Stream.name == stream_name).get()

        if not stream:
            self.error(404)
            return

        total_pages = int(math.ceil(stream.photos.count()*1.0/per_page))
        photos = stream.photos.order(-Photo.creation_date).fetch(per_page, offset=per_page * (page - 1))
        photo_urls = ['/get_photo?img_id='+p.key.urlsafe() for p in photos]

        vr = ViewRecord(stream = stream.key)
        vr.put()

        cover_url = stream.cover_url
        if not cover_url:
            cover_url = DEFAULT_STREAM_COVER_URL

        stream.put()

        result = {'stream_name': stream_name,\
                'cover_url': cover_url,\
                'total_pages': total_pages,\
                'page': page,\
                'per_page': per_page,\
                'photo_urls': photo_urls}
        self.response.set_status(200)
        self.response.out.write(json.dumps(result))

    def all_streams(self):
        self.response.headers['Content-Type'] = 'application/json'
        stream_name = self.request.get('stream_name', '')
        streams = []
        if stream_name:
            streams = [ s for s in Stream.query().fetch() if (stream_name in s.name) ]
        else:
            streams = Stream.query().fetch()
        result = []
        for s in streams:
            cover_url=s.cover_url
            if not cover_url:
                cover_url = DEFAULT_STREAM_COVER_URL
            result.append({'name': s.name, 'cover_url': cover_url})
        self.response.out.write(json.dumps(result))
        self.response.set_status(200)

    def trending_streams(self):
        self.response.headers['Content-Type'] = 'application/json'

        duration = int(self.request.get('duration', 60*60))
        streams = Stream.query().fetch()
        freq = {}
        bound = datetime.datetime.now() - datetime.timedelta(0, duration)
        for s in streams:
            c = s.view_records.filter(ViewRecord.date > bound).count()
            cover_url = s.cover_url
            if not cover_url:
                cover_url = DEFAULT_STREAM_COVER_URL
            freq[s.name] = (c, cover_url)
        series = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
        result=[]
        for s in series:
            element = {}
            element['name']=s[0]
            element['count']=s[1][0]
            element['cover_url']=s[1][1]
            result.append(element)

        self.response.out.write(json.dumps(result))
        self.response.set_status(200)

    def management(self):
        self.response.headers['Content-Type'] = 'application/json'
        def get_stream_data(stream):
            name = stream.name
            number_of_photos = stream.photos.count()
            last_new_photo_date = ''
            if number_of_photos > 0:
                last_new_photo_date = stream.photos.order(-Photo.creation_date).get().creation_date
                last_new_photo_date = str(last_new_photo_date)
            else:
                last_new_photo_date = time.strftime('%m/%d/%Y', time.gmtime(0))

            return {'name':name, 'number_of_photos':number_of_photos,\
                    'number_of_views':stream.view_records.count(), 'last_new_photo_date':last_new_photo_date}

        if gusers.get_current_user():
            user = User.query().filter(User.email == gusers.get_current_user().email()).get()
            owned_streams = [ get_stream_data(s) for s in user.owned_streams.fetch() ]
            subscribed_streams = [ get_stream_data(k.get()) for k in user.subscription_list ]

            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps({ 'owned_streams': owned_streams,\
                'subscribed_streams': subscribed_streams}))

        else:
            self.response.set_status(403)
            self.response.out.write(json.dumps({ 'error': 'not logged in' }))

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

            for rname in remove_list:
                stream = Stream.query().filter(Stream.name == rname).get()
                if not stream:
                    continue
                key = stream.key
                if stream.owner.get().email == user_email:
                    for u in stream.members.fetch():
                        u.subscription_list.remove(key)
                        u.put()
                    key.delete()

            user = User.query().filter(User.email == user_email).get()
            for unname in unsubscribe_list:
                stream = Stream.query().filter(Stream.name == unname).get()
                key = stream.key
                if key in user.subscription_list:
                    user.subscription_list.remove(key)
                user.put()
            self.response.set_status(200)
        else:
            self.response.set_status(403)
            self.response.out.write(json.dumps({ 'error': 'not logged in' }))

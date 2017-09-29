#!/usr/bin/env python

# [START imports]
import os
import urllib

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_STREAM_NAME = 'default_stream'

def stream_key(stream_name=DEFAULT_STREAM_NAME):
    return ndb.Key('Stream', stream_name)

class Stream(ndb.Model):
    name = ndb.StringProperty()
    number_of_views = ndb.IntegerProperty()
    cover = ndb.BlobProperty()

class Photo(ndb.Model):
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    data = ndb.BlobProperty()
    stream = ndb.StructuredProperty(Stream)




# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

class PhotoUpload(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('photoUpload.html')
        self.response.write(template.render({}))
# [END main_page]

class StreamCreator(webapp2.RequestHandler):

    def post(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        cover = self.request.get('cover_image') # TODO: can be empty
        stream = Stream()
        stream.cover_image = cover;
        stream.number_of_views = 0
        stream.put()
        query_params = {'stream_name': stream_name}
        self.redirect('/StreamView?' + urllib.urlencode(query_params))

class StreamViewer(webapp2.RequestHandler):

    def get(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        photos_query = Photo.query(
            ancestor=stream_key(stream_name))#TODO: the shitty index .order(-Photo.creation_date)
        photos = photos_query.fetch(10)
        photo_urls = [p.key.urlsafe() for p in photos]

        template_values = {'stream_name': stream_name, 'photo_urls': photo_urls}
        template = JINJA_ENVIRONMENT.get_template('stream.html')
        self.response.write(template.render(template_values))
        

class PhotoCreator(webapp2.RequestHandler):

    def post(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        photo = Photo(parent=stream_key(stream_name))
        photo_data = self.request.get('photo_data')
        photo.data = photo_data
        photo.put()
        query_params = {'stream_name': stream_name}
        self.redirect('/StreamView?' + urllib.urlencode(query_params))

class PhotoViewer(webapp2.RequestHandler):

    def get(self):
        photo_key = ndb.Key(urlsafe=self.request.get('img_id'))
        photo = photo_key.get()
        if photo.data:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(photo.data)
        else:
            pass #TODO
        

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/CreateStream', StreamCreator),
    ('/StreamView', StreamViewer),
    ('/PhotoUpload', PhotoUpload),
    ('/submitPhoto', PhotoCreator),
    ('/img', PhotoViewer),
], debug=True)
# [END app]

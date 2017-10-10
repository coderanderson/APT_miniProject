import webapp2
import urllib
from codes.models import *
from google.appengine.ext import ndb


class PhotoAPIController(webapp2.RequestHandler):

    def create(self):
        self.response.headers['Content-Type'] = 'application/json'

        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        stream = Stream.query().filter(Stream.name == stream_name).get()
        if not stream:
            self.response.set_status(400)
            self.response.out.write(json.dumps({'error': 'stream not found'}))

        photo = Photo(stream=stream.key)
        photo_data = self.request.get('photo_data')
        photo.data = photo_data
        photo.put()
        self.response.set_status(200)

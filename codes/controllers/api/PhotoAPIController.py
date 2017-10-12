import webapp2
import urllib
from codes.models import *
from google.appengine.ext import ndb

class PhotoAPIController(webapp2.RequestHandler):
    def create(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        photo_data = self.request.get('photo_data')

        result = Photo.store(stream_name, photo_data)

        self.response.headers['Content-Type'] = 'application/json'
        if 'error' in result:
            self.response.set_status(404)
            self.response.out.write(json.dumps({'error': result['error']}))
        else:
            self.response.set_status(200)
            self.response.out.write(json.dumps({}))

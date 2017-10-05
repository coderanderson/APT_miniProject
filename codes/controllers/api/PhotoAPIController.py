import webapp2
import urllib
from codes.models.Models import *
from google.appengine.ext import ndb

class PhotoController(webapp2.RequestHandler):
    def view(self):
        try:
            photo_key = ndb.Key(urlsafe=self.request.get('img_id'))
            photo = photo_key.get()
            if photo.data:
                self.response.headers['Content-Type'] = 'image/png'
                self.response.out.write(photo.data)
            else:
                raise 404
        except:
            self.error(404)

    def create(self):
        self.response.headers['Content-Type'] = 'application/json'

        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        stream = Stream.query().filter(Stream.name == stream_name).get()
        if not stream:
            response.error(400)
            self.response.out.write(json.dumps({'error': 'stream not found'}))

        photo = Photo(stream = stream.key)
        photo_data = self.request.get('photo_data')
        photo.data = photo_data
        photo.put()
        self.response.set_status(200)


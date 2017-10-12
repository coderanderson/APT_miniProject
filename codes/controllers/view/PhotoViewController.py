import webapp2
import urllib
from codes.models import *
from google.appengine.ext import ndb

class PhotoViewController(webapp2.RequestHandler):
    view_route = '/get_photo'

    @classmethod
    def generate_url_of_photo(cls, p):
        query_params = {'img_id': p.key.urlsafe()}
        return cls.view_route + '?' + urllib.urlencode(query_params)

    def view(self):
        try:
            photo_key = ndb.Key(urlsafe=self.request.get('img_id'))
            photo = photo_key.get()
            if photo.data:
                self.response.headers['Content-Type'] = 'image/png'
                self.response.out.write(photo.data)
            else:
                self.error(404)
        except:
            self.error(404)

    def create(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        photo_data = self.request.get('photo_data')

        result = Photo.store(stream_name, photo_data)
        if 'error' in result:
            self.response.set_status(404)
            self.response.out.write(json.dumps({'error': result['error']}))
        else:
            query_params = {'stream_name': stream_name, 'All':0}
            self.redirect('/view_stream?' + urllib.urlencode(query_params))

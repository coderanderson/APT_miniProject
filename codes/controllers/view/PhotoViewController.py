import webapp2
import urllib
from codes.models.Models import *
from google.appengine.ext import ndb

class PhotoViewController(webapp2.RequestHandler):
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

    def show_upload_menu(self):
        template = PhotoController.JINJA_ENVIRONMENT.get_template('upload_photo.html')
        self.response.write(template.render({}))

    def create(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        photo = Photo(parent=stream_key(stream_name))
        photo_data = self.request.get('photo_data')
        photo.data = photo_data
        photo.put()
        query_params = {'stream_name': stream_name}
        self.redirect('/view_stream?' + urllib.urlencode(query_params))


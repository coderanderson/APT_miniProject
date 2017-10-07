import webapp2
import urllib
from codes.models import *
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
        stream = Stream.query().filter(Stream.name == stream_name).get()
        if not stream:
            self.response.set_status(400)
            self.response.out.write(json.dumps({'error': 'stream not found'}))

        photo = Photo(stream = stream.key)
        photo_data = self.request.get('photo_data')
        photo.data = photo_data
        photo.put()
        self.response.set_status(200)
        query_params = {'stream_name': stream_name, 'All':1}
        self.redirect('/view_stream?' + urllib.urlencode(query_params))


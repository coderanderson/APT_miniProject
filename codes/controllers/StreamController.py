import webapp2
import urllib
from codes.models.Stream import *
from codes.models.Photo import *
from google.appengine.ext import ndb

class StreamController(webapp2.RequestHandler):
    def view(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        photos_query = Photo.query(
            ancestor = stream_key(stream_name)).order(-Photo.creation_date)
        photos = photos_query.fetch(10)
        photo_urls = [p.key.urlsafe() for p in photos]

        stream = Stream.query().filter(Stream.name == stream_name).get()

        template_values = {'stream_name': stream_name,\
                'cover_url': stream.key.urlsafe(),
                'photo_urls': photo_urls}
        template = StreamController.JINJA_ENVIRONMENT.get_template('stream.html')
        self.response.write(template.render(template_values))

    def create(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        cover = self.request.get('cover')
        stream = Stream()
        if cover:
            stream.cover = cover
        stream.name = stream_name
        stream.number_of_views = 0
        stream.put()
        query_params = {'stream_name': stream_name}
        self.redirect('/view_stream?' + urllib.urlencode(query_params))

    def show_create_menu(self):
        template = StreamController.JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

    def view_cover(self):
        stream_key = ndb.Key(urlsafe=self.request.get('cover_id'))
        stream = stream_key.get()
        self.response.headers['Content-Type'] = 'image/png'
        if stream.cover:
            self.response.out.write(stream.cover)
        else:
            self.redirect('/static_files/img/no_cover.png')

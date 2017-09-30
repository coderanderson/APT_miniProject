import webapp2
import urllib
from codes.models.Stream import *
from codes.models.Photo import *
from codes.models.User import *
from google.appengine.ext import ndb
from google.appengine.api import users as gusers

class StreamController(webapp2.RequestHandler):
    def view(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        photos_query = Photo.query(
            ancestor = stream_key(stream_name)).order(-Photo.creation_date)
        photos = photos_query.fetch(10)
        photo_urls = [p.key.urlsafe() for p in photos]

        stream = Stream.query().filter(Stream.name == stream_name).get()
        stream.number_of_views += 1

        cover_url = stream.cover_url
        if not cover_url:
            cover_url = DEFAULT_STREAM_COVER_URL

        stream.put()

        template_values = {'stream_name': stream_name,\
                'cover_url': cover_url,
                'photo_urls': photo_urls}
        template = StreamController.JINJA_ENVIRONMENT.get_template('stream.html')
        self.response.write(template.render(template_values))

    def create(self):
        if gusers.get_current_user():
            stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
            cover_url = self.request.get('cover_url')
            stream = Stream()
            if cover_url:
                stream.cover_url = cover_url
            stream.name = stream_name
            user = User(email=owner_email)
            user.put()
            stream.owner = user
            stream.number_of_views = 0
            stream.put()
            query_params = {'stream_name': stream_name}
            self.redirect('/view_stream?' + urllib.urlencode(query_params))
        else:
            self.error(403)

    def show_create_menu(self):
        template = StreamController.JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

    def show_manage_menu(self):
        def get_stream_data(stream):
            name = stream.name
            number_of_photos = len(stream.photos)
            number_of_views = stream.number_of_views
            last_new_photo_data = ''
            if len(stream.photos) > 0:
                last_new_photo_data = stream.photos[0].creation_date
            else:
                last_new_photo_data = stream.photos.order(-Photo.creation_date).get().creation_date

            return {'name':name, 'number_of_photos':number_of_photos,\
                    'number_of_views':number_of_views, 'last_new_photo_data':last_new_photo_data}

        if gusers.get_current_user():
            user = User.query().filter(User.email == gusers.get_current_user().email).get()
            owned_streams = [ get_stream_data(s) for s in user.owned_streams ]
            subscribed_streams = [ get_stream_data(k.get()) for k in user.subscription_list ]

            template = StreamController.JINJA_ENVIRONMENT.get_template('manage.html')

            self.response.write(template.render({ 'owned_streams': owned_streams,
                'subscribed_streams': subscribed_streams}))

        else:
            self.error(403)

    def delete_selected_streams(self):
        remove_list = self.request.get('streams', allow_multiple=True)
        make_management_changes(self, remove_list, [])

    def unsubscribe_selected_streams(self):
        unsubscribe_list = self.request.get('streams', allow_multiple=True)
        make_management_changes(self, [], unsubscribe_list)

    def make_management_changes(self, remove_list, unsubscribe_list):
        if gusers.get_current_user():

            user_email = gusers.get_current_user().email()

            for rname in remove_list:
                stream = Stream.query().filter(Stream.name == rname).get()
                key = stream.key
                if stream.owner.email == user_email:
                    for u in stream.members():
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
            self.redirect('/manage')
        else:
            self.error(403)

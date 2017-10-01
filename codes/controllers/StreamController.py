import webapp2
import urllib
from codes.models.Stream import *
from codes.models.Photo import *
from codes.models.User import *
from google.appengine.ext import ndb
from google.appengine.api import users as gusers
from google.appengine.api import search

STREAM_INDEX = 'stream_index'

class StreamController(webapp2.RequestHandler):
    def view(self):
        per_page = 10
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        page = self.request.get('page', 0)
        photos_query = Photo.query(
            ancestor = stream_key(stream_name),).order(-Photo.creation_date)

        total_pages = math.ceil(photos_query.count()/per_page)

        photos = photos_query.fetch(per_page, offset=per_page * page)
        photo_urls = [p.key.urlsafe() for p in photos]

        stream = Stream.query().filter(Stream.name == stream_name).get()
        vr = ViewRecord(stream=stream)
        vr.put()

        cover_url = stream.cover_url
        if not cover_url:
            cover_url = DEFAULT_STREAM_COVER_URL

        stream.put()

        template_values = {'stream_name': stream_name,\
                'cover_url': cover_url,
                'range': total_pages,
                'photo_urls': photo_urls}
        template = StreamController.JINJA_ENVIRONMENT.get_template('stream.html')
        self.response.write(template.render(template_values))

    def create(self):
        if gusers.get_current_user():
            stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
            cover_url = self.request.get('cover_url', '')

            user = User(email=gusers.get_current_user().email())
            user.put()
            stream = Stream()
            if cover_url:
                stream.cover_url = cover_url
            stream.name = stream_name
            stream.tags = self.request.get('tags', '')
            stream.owner = user
            stream.put()
            search.Index(name=STREAM_INDEX).put(stream)

            invitee_emails = self.request.get('invitee_emails', '')
            invitee_emails = [ e.strip() for e in invitee_emails.split(',') ]
            invitation_link = self.request.host_url + '/invite?stream_name=' + stream_name
            email_body = StreamController.JINJA_ENVIRONMENT.get_template('invitation.html')
            email_body = email_body.render({'invitation_link': invitation_link,\
                'message': message, 'stream_name': 'stream_name'})

            for e in invitee_emails:
                mail.send_mail(sender=gusers.get_current_user().email(), to=e,\
                    subject="Stream Invitation",body=email_body)

            self.redirect('/manage')
        else:
            self.error(403)

    def show_create_menu(self):
        template = StreamController.JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

    def all_streams(self):
        stream_name = self.request.get('stream_name', '')
        streams = []
        if stream_name:
            streams = search.Index(STREAM_INDEX).search(stream_name)
        else:
            streams = Stream.query().fetch()
        result = []
        for s in streams:
            cover_url=s.cover_url
            if not cover_url:
                cover_url = DEFAULT_STREAM_COVER_URL
            result.append({'name': s.name, 'cover_url': cover_url})
        template = StreamController.JINJA_ENVIRONMENT.get_template('all_stream.html')
        self.response.write(template.render({'streams': result}))

    def invite(self):
        if gusers.get_current_user():
            stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
            stream = Stream.query().filter(Stream.name == stream_name).get()
            user = User.query().filter(User.email == gusers.get_current_user().email).get()
            if stream:
                if not user:
                    user = User(email = gusers.get_current_user().email, subscription_list=[])
                user.subscription_list.append(stream.key)
                user.put()
            else:
                self.error(400)
        else:
            self.redirect(gusers.create_login_url('/invite?stream_name=' + stream_name))

    def show_manage_menu(self):
        def get_stream_data(stream):
            name = stream.name
            number_of_photos = len(stream.photos)
            last_new_photo_data = ''
            if len(stream.photos) > 0:
                last_new_photo_data = stream.photos[0].creation_date
            else:
                last_new_photo_data = stream.photos.order(-Photo.creation_date).get().creation_date

            return {'name':name, 'number_of_photos':number_of_photos,\
                    'number_of_views':len(stream.view_records), 'last_new_photo_data':last_new_photo_data}

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
                search.Index(name=STREAM_INDEX).delete(stream)
                key = stream.key
                if key in user.subscription_list:
                    user.subscription_list.remove(key)
                user.put()
            self.redirect('/manage')
        else:
            self.error(403)

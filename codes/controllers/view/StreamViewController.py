import webapp2
import urllib
import codes
import math
import datetime
from codes.models import *
from codes.controllers.view.UserViewController import UserViewController
from google.appengine.ext import ndb
from google.appengine.api import users as gusers
from google.appengine.api import mail

STREAM_INDEX = 'stream_index'


class StreamViewController(webapp2.RequestHandler):

    def create(self):
        from_view = True
        if gusers.get_current_user():
            stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
            cover_url = self.request.get('cover_url', '')
            message = self.request.get('message', '')
            invitee_emails = self.request.get('invitee_emails', '')
            stream = Stream.query().filter(Stream.name == stream_name).get()

            if stream:
                result = {
                    'signurl': gusers.create_logout_url('/'),
                    'signtext': 'Logout',
                    'error': 'duplicate stream name'
                }
                template = StreamViewController.JINJA_ENVIRONMENT.get_template(
                    'error.html')
                self.response.write(template.render(result))
            else:
                user = User.query().filter(User.email == gusers.get_current_user().email()).get()
                stream = Stream()
                if cover_url:
                    stream.cover_url = cover_url
                stream.name = stream_name
                stream.tags = self.request.get('tags', '')
                stream.owner = user.key
                stream.put()
                user.subscription_list.append(stream.key)
                user.put()
                stream.owner = user.key
                stream.put()

                invitee_emails = [
                    e.strip() for e in invitee_emails.split(',') if e.strip() != '']
                invitation_link = self.request.host_url + '/invite?stream_name=' + stream_name
                email_body = codes.controllers.view.StreamViewController.\
                    StreamViewController.JINJA_ENVIRONMENT.get_template(
                        'invitation.html')
                email_body = email_body.render({'invitation_link': invitation_link,
                                                'message': message, 'stream_name': stream_name})

                for e in invitee_emails:
                    mail.send_mail(sender=gusers.get_current_user().email(), to=e,
                                   subject="Stream Invitation", body='', html=email_body)

                if not from_view:
                    self.response.set_status(200)
                else:
                    self.redirect('/manage')
        else:
            if not from_view:
                self.error(403)
            else:
                result = {
                    'signurl': gusers.create_login_url('/'),
                    'signtext': 'Login',
                    'error': 'you should login first'
                }
                template = StreamViewController.JINJA_ENVIRONMENT.get_template(
                    'error.html')
                self.response.write(template.render(result))

    def show_create_menu(self):
        user = gusers.get_current_user()
        if user:
            url = gusers.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            _user = User.query().filter(User.email == gusers.get_current_user().email()).get()
            if not _user:
                _user = User(email=gusers.get_current_user().email())
                _user.put()
        else:
            url = gusers.create_login_url(self.request.uri)
            url_linktext = 'Login'
        result = {
            'signurl': url,
            'signtext': url_linktext,
        }
        template = StreamViewController.JINJA_ENVIRONMENT.get_template(
            'create_stream.html')
        self.response.write(template.render(result))

    def view(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        page = int(self.request.get('page', 1))
        per_page = int(self.request.get('per_page', 10))
        All = int(self.request.get('All', '0'))

        stream = Stream.query().filter(Stream.name == stream_name).get()

        if not stream:
            self.error(404)
            return

        total_pages = int(math.ceil(stream.photos.count() * 1.0 / per_page))
        photos = stream.photos.order(-Photo.creation_date).fetch(
            per_page, offset=per_page * (page - 1))
        photo_urls = ['/get_photo?img_id=' + p.key.urlsafe() for p in photos]

        vr = ViewRecord(stream=stream.key)
        vr.put()

        cover_url = stream.cover_url
        if not cover_url:
            cover_url = DEFAULT_STREAM_COVER_URL

        stream.put()

        user = gusers.get_current_user()
        if user:
            url = gusers.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            _user = User.query().filter(User.email == gusers.get_current_user().email()).get()
            if not _user:
                _user = User(email=gusers.get_current_user().email())
                _user.put()
        else:
            url = gusers.create_login_url(self.request.uri)
            url_linktext = 'Login'
        result = {
            'signurl': url,
            'All': All,
            'signtext': url_linktext,
            'stream_name': stream_name,
            'cover_url': cover_url,
            'total_pages': total_pages,
            'page': page,
            'per_page': per_page,
            'photo_urls': photo_urls}
        template = StreamViewController.JINJA_ENVIRONMENT.get_template(
            'stream.html')
        self.response.write(template.render(result))

    def all_streams(self):
        stream_name = self.request.get('stream_name', '')
        streams = []
        if stream_name:
            streams = [s for s in Stream.query().fetch()
                       if (stream_name in s.name)]
        else:
            streams = Stream.query().fetch()
        result = []
        for s in streams:
            cover_url = s.cover_url
            if not cover_url:
                cover_url = DEFAULT_STREAM_COVER_URL
            result.append({'name': s.name, 'cover_url': cover_url})
        user = gusers.get_current_user()
        if user:
            url = gusers.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            _user = User.query().filter(User.email == gusers.get_current_user().email()).get()
            if not _user:
                _user = User(email=gusers.get_current_user().email())
                _user.put()
        else:
            url = gusers.create_login_url(self.request.uri)
            url_linktext = 'Login'
        covers = []
        names = []
        for o in result:
            covers.append(o['cover_url'])
            names.append(o['name'])
        template_values = {
            'signurl': url,
            'signtext': url_linktext,
            'names': names, 'covers': covers}
        template = StreamViewController.JINJA_ENVIRONMENT.get_template(
            'allStreams.html')
        self.response.write(template.render(template_values))

    def update_trending_info(self):
        duration = int(self.request.get('interval', 60 * 60))
        from_view = True
        if gusers.get_current_user():
            user = User.query().filter(User.email == gusers.get_current_user().email()).get()
            if duration is 0:
                user.getting_trendings = False
            else:
                user.getting_trendings = True
                user.trendings_interval = duration
                user.last_trending_sent = datetime.datetime.now()
            user.put()
            self.redirect('/trending')
        else:
            result = {
                'signurl': gusers.create_login_url('/'),
                'signtext': 'Login',
                'error': 'you should login first'
            }
            template = StreamViewController.JINJA_ENVIRONMENT.get_template(
                'error.html')
            self.response.write(template.render(result))

    def show_trending_streams(self):
        streams = []
        streams = TrendingStream.query().fetch()
        result = []
        for s in streams:
            cover_url = s.cover_url
            if not cover_url:
                cover_url = DEFAULT_STREAM_COVER_URL
            result.append(
                {'name': s.name, 'cover_url': cover_url, 'count': s.count})
        user = gusers.get_current_user()
        if user:
            url = gusers.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            _user = User.query().filter(User.email == gusers.get_current_user().email()).get()
            if not _user:
                _user = User(email=gusers.get_current_user().email())
                _user.put()
        else:
            url = gusers.create_login_url(self.request.uri)
            url_linktext = 'Login'
        covers = []
        names = []
        counts = []
        for o in result:
            covers.append(o['cover_url'])
            names.append(o['name'])
            counts.append(o['count'])
        template_values = {
            'signurl': url,
            'signtext': url_linktext,
            'names': names, 'covers': covers, 'counts': counts}
        template = StreamViewController.JINJA_ENVIRONMENT.get_template(
            'trending.html')
        self.response.write(template.render(template_values))

    def invite(self):
        if gusers.get_current_user():
            stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
            stream = Stream.query().filter(Stream.name == stream_name).get()
            user = User.query().filter(User.email == gusers.get_current_user().email()).get()
            if stream:
                if not stream.key in user.subscription_list:
                    user.subscription_list.append(stream.key)
                    user.put()
                self.redirect('/view_stream?stream_name=' + stream_name)
            else:
                self.error(400)
        else:
            self.redirect(gusers.create_login_url('/'))

    def search_stream(self):
        query = self.request.get('search', '')
        if query:
            streams = [s for s in Stream.query().fetch() if (
                query in s.name or query in s.tags)]
        else:
            streams = []
        user = gusers.get_current_user()
        if user:
            url = gusers.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            _user = User.query().filter(User.email == gusers.get_current_user().email()).get()
            if not _user:
                _user = User(email=gusers.get_current_user().email())
                _user.put()
        else:
            url = gusers.create_login_url(self.request.uri)
            url_linktext = 'Login'

        result = []
        for s in streams:
            cover_url = s.cover_url
            if not cover_url:
                cover_url = DEFAULT_STREAM_COVER_URL
            result.append({'name': s.name, 'cover_url': cover_url})

        covers = []
        names = []
        for o in result:
            covers.append(o['cover_url'])
            names.append(o['name'])
        template_values = {
            'signurl': url,
            'signtext': url_linktext,
            'query': query,
            'count': len(streams),
            'names': names,
            'covers': covers
        }
        template = StreamViewController.JINJA_ENVIRONMENT.get_template(
            'search.html')
        self.response.write(template.render(template_values))

    def show_manage_menu(self):
        template_values = {}
        template_values.update(UserViewController.get_login_info(self))
        template = StreamViewController.JINJA_ENVIRONMENT.get_template(
            'manage.html')
        self.response.write(template.render(template_values))

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

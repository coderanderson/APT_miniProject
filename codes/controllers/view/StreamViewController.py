import webapp2
import urllib
import codes
from codes.controllers.view.UserViewController import UserViewController
from codes.controllers.view.PhotoViewController import PhotoUploadHandler
from codes.models import *
from google.appengine.api import users as gusers

STREAM_INDEX = 'stream_index'

class StreamViewController(webapp2.RequestHandler):
    def create(self):
        login_info = UserViewController.get_login_info(self)

        if gusers.get_current_user():
            stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
            cover_url = self.request.get('cover_url', '')
            message = self.request.get('message', '')
            invitee_emails = self.request.get('invitee_emails', '')
            invitee_emails = [ e.strip() for e in invitee_emails.split(',') if e.strip()!='' ]
            tags = self.request.get('tags', '')

            create_result = Stream.create(stream_name, gusers.get_current_user().email(), cover_url,\
                    message, invitee_emails, self.request.host_url, tags)

            if 'error' in create_result:
                result = {'error': create_result['error']}
                result.update(login_info)
                template = StreamViewController.JINJA_ENVIRONMENT.get_template('error.html')
                self.response.write(template.render(result))
            else:
                self.redirect(StreamViewController.manage_route)
        else:
            result = {'error': UserViewController.login_error}
            result.update(login_info)
            template = StreamViewController.JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render(result))

    def show_create_menu(self):
        template_values = UserViewController.get_login_info(self)
        template = StreamViewController.JINJA_ENVIRONMENT.get_template('create_stream.html')
        self.response.write(template.render(template_values))

    view_route = '/view_stream'
    def view(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
        page = int(self.request.get('page', 1))
        per_page = int(self.request.get('per_page', 10))
        All = int(self.request.get('All', '0'))

        result = Stream.view(stream_name, page, per_page, All==1)
        result.update({ 'invite_route': StreamViewController.invite_route, 'view_route': StreamViewController.view_route })
        result['All'] = All
        if not result:
            self.error(404)
        else:
            result.update(UserViewController.get_login_info(self))
            result['photo_upload_url'] = PhotoUploadHandler.upload_url
            template = StreamViewController.JINJA_ENVIRONMENT.get_template('stream.html')
            self.response.write(template.render(result))
        
    def view_all(self):
        result = Stream.all_streams_matching('')
        covers = [o['cover_url'] for o in result]
        names = [o['name'] for o in result]
        template_values = {'names': names, 'covers':covers}
        template_values.update(UserViewController.get_login_info(self))
        template = StreamViewController.JINJA_ENVIRONMENT.get_template('all_streams.html')
        self.response.write(template.render(template_values))

    def update_trending_preferences(self):
        duration = int(self.request.get('interval', 60*60))
        from_view = True
        if gusers.get_current_user():
            User.update_trending_preferences(gusers.get_current_user().email(), duration)
            self.redirect(StreamViewController.trendings_show_route)
        else:
            result = {'error': UserViewController.login_error}
            result.update(UserViewController.get_login_info(self))
            template = StreamViewController.JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render(result))

    trendings_show_route = '/trending'
    def show_trending_streams(self):
        user_email = ''
        if gusers.get_current_user():
            user_email = gusers.get_current_user().email()
        template_values = TrendingStream.get_current_trending_streams(user_email)
        template_values.update(UserViewController.get_login_info(self))
        template = StreamViewController.JINJA_ENVIRONMENT.get_template('trending.html')
        self.response.write(template.render(template_values))

    @classmethod
    def create_invitation_link(cls, host, stream_name):
        query_params = {'stream_name': stream_name}
        invitation_link = host + cls.invite_route + '?' + urllib.urlencode(query_params)

    invite_route = '/invite'
    manage_route = '/manage'
    def handle_invitation(self):
        if gusers.get_current_user():
            stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)
            user_email = gusers.get_current_user().email()
            added = Stream.add_user_to_stream(stream_name, user_email)
            if added:
                query_params = {'stream_name': stream_name}
                self.redirect(StreamViewController.view_route + '?' + urllib.urlencode(query_params))
            else:
                self.error(404)
        else:
            self.redirect(gusers.create_login_url('/'))

    def search_stream(self):
        query = self.request.get('search', '')
        result = []
        if query:
            result = Stream.all_streams_matching(query)
        covers = [o['cover_url'] for o in result]
        names = [o['name'] for o in result]
        template_values = {'names': names, 'covers':covers, 'query': query, 'count': len(result)}
        template_values.update(UserViewController.get_login_info(self))
        template = StreamViewController.JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))

    def show_manage_menu(self):
        template_values = {}
        template_values.update(UserViewController.get_login_info(self))
        if gusers.get_current_user():
            template = StreamViewController.JINJA_ENVIRONMENT.get_template('manage.html')
        else:
            template = StreamViewController.JINJA_ENVIRONMENT.get_template('error.html')
            template_values = {'error': UserViewController.login_error}
        template_values.update(UserViewController.get_login_info(self))
        self.response.write(template.render(template_values))

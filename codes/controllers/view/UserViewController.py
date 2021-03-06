import webapp2
import datetime
from google.appengine.api import users as gusers
from codes.models import *

class UserViewController(webapp2.RequestHandler):

    login_error = 'you should login first'
    @classmethod
    def get_login_info(cls, callee, explicit_uri=None):
        uri = callee.request.uri
        if explicit_uri:
            uri = explicit_uri
        user = gusers.get_current_user()
        if user:
            url = gusers.create_logout_url(uri)
            url_linktext = 'Logout'
            _user = User.query().filter(User.email == gusers.get_current_user().email()).get()
            if not _user:
                _user = User(email=gusers.get_current_user().email())
                _user.getting_trendings = False
                _user.trendings_interval = 0
                _user.last_trending_sent = datetime.datetime.now()
                _user.put()
        else:
            url = gusers.create_login_url(uri)
            url_linktext = 'Login'
        result = {
            'signurl': url,
            'signtext': url_linktext,
        }
        return result

    def front_page(self):

        template_values = {
            'login_page': True
        }
        template_values.update(UserViewController.get_login_info(self))
        template = UserViewController.JINJA_ENVIRONMENT.get_template(
            'login.html')
        self.response.write(template.render(template_values))
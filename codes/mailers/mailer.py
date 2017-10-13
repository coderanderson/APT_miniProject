import codes
from urlparse import urlparse
from codes.controllers.view.StreamViewController import StreamViewController

from urllib import urlencode
import httplib2

MAILGUN_DOMAIN_NAME = 'sandbox7dddd882d12f4e6d89c7469f34b24e4c.mailgun.org'
MAILGUN_API_KEY = 'key-3b89e1ad9553f1d9ca0971f486a6c388'

class Mailer():
    JINJA_ENVIRONMENT = ''

    @classmethod
    def send_invitation_emails(cls, host, stream_name, message, current_user_email, invitee_emails):
        invitation_link = StreamViewController.create_invitation_link(host, stream_name)
        print "moez: invitation link: ", invitation_link, host, stream_name
        email_body = cls.JINJA_ENVIRONMENT.get_template('invitation.html')
        email_body = email_body.render({'invitation_link': invitation_link,\
            'message': message, 'stream_name': stream_name})

        for e in invitee_emails:
            cls.send_email('inviter', 'inviter', e, "Stream Invitation", '', email_body)

    @classmethod
    def send_trending_report_emails(cls, host, view_route, names, recipients):
        pass
        email_body = cls.JINJA_ENVIRONMENT.get_template('trending_report.html')
        email_body = email_body.render({'names': names, 'host': host, 'view_route': view_route})
        sender = 'anything@' + urlparse(host).netloc
        for e in recipients:
            cls.send_email('reporter', 'reporter', e, "Trending Streams", '', email_body)

    @classmethod
    def send_email(cls, sender_name, sender_uid, recipient, subject, text, html):
        http = httplib2.Http()
        http.add_credentials('api', MAILGUN_API_KEY)
    
        url = 'https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN_NAME)
        data = {
            'from': '{} <{}@{}>'.format(sender_name, sender_uid, MAILGUN_DOMAIN_NAME),
            'to': recipient,
            'subject': subject,
            'text': text,
            'html': html
        }
    
        resp, content = http.request(
            url, 'POST', urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"})
    
        return resp.status == 200

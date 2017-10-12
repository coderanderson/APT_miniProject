import codes
from urlparse import urlparse
from codes.controllers.view.StreamViewController import StreamViewController
from google.appengine.api import mail #TODO

class Mailer():
    JINJA_ENVIRONMENT = ''

    @classmethod
    def send_invitation_emails(cls, host, stream_name, message, current_user_email, invitee_emails):
        invitation_link = StreamViewController.create_invitation_link(host, stream_name)
        email_body = cls.JINJA_ENVIRONMENT.get_template('invitation.html')
        email_body = email_body.render({'invitation_link': invitation_link,\
            'message': message, 'stream_name': stream_name})

        for e in invitee_emails:
            mail.send_mail(sender=current_user_email, to=e,\
                subject="Stream Invitation",body='', html=email_body)

    @classmethod
    def send_trending_report_emails(cls, host, view_route, names, recipients):
        pass
        email_body = cls.JINJA_ENVIRONMENT.get_template('trending_report.html')
        email_body = email_body.render({'names': names, 'host': host, 'view_route': view_route})
        sender = 'anything@' + urlparse(host).netloc
        for e in recipients:
            mail.send_mail(sender=sender, to=e,\
                subject="Trending Streams",body='', html=email_body)

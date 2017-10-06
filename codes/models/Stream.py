from google.appengine.ext import ndb
import codes
import datetime

DEFAULT_STREAM_NAME = 'default_stream'
DEFAULT_STREAM_COVER_URL = '/static_files/img/no_cover.png'

class Stream(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    cover_url = ndb.StringProperty()
    tags = ndb.TextProperty()
    owner = ndb.KeyProperty(kind='User')

    @property
    def photos(self):
        return codes.models.Photo.gql("WHERE stream = :1", self.key)
    @property
    def members(self):
        return codes.models.User.gql("WHERE subscription_list = :1", self.key)
    @property
    def view_records(self):
        return codes.models.ViewRecord.gql("WHERE stream = :1", self.key)

    @classmethod
    def remove_old_view_records(cls, duration=3600):
        bound = datetime.datetime.now() - datetime.timedelta(0, duration)
        keys = [ v.key for v in codes.models.ViewRecord.query().filter(codes.models.ViewRecord.date < bound).fetch() ]
        for k in keys:
            k.delete()
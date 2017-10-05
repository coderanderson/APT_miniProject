from google.appengine.ext import ndb
from codes.models.User import User
# from codes.models.ViewRecord import ViewRecord

DEFAULT_STREAM_NAME = 'default_stream'
DEFAULT_STREAM_COVER_URL = '/static_files/img/no_cover.png'

def stream_key(stream_name=DEFAULT_STREAM_NAME):
    return ndb.Key('Stream', stream_name)

class Stream(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    cover_url = ndb.StringProperty()
    tags = ndb.TextProperty()
    owner = ndb.KeyProperty(kind=User)#, collection_name='owned_streams')

    @property
    def members(self):
        return User.gql("WHERE streams = :1", self.key())
    @property
    def view_records(self):
        return ViewRecord.gql("WHERE streams = :1", self.key())

class ViewRecord(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True)
    stream = ndb.KeyProperty(kind=Stream)#, collection_name='view_records')

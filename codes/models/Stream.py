from google.appengine.ext import ndb


DEFAULT_STREAM_NAME = 'default_stream'
DEFAULT_STREAM_COVER_URL = '/static_files/img/no_cover.png'

def stream_key(stream_name=DEFAULT_STREAM_NAME):
    return ndb.Key('Stream', stream_name)

class Stream(ndb.Model):
    name = ndb.StringProperty()
    number_of_views = ndb.IntegerProperty()
    cover_url = ndb.StringProperty()
    owner = db.ReferenceProperty(User, collection_name='owned_streams')

    @property
        def members(self):
            return Contact.gql("WHERE streams = :1", self.key())

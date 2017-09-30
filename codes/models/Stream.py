from google.appengine.ext import ndb

DEFAULT_STREAM_NAME = 'default_stream'

def stream_key(stream_name=DEFAULT_STREAM_NAME):
    return ndb.Key('Stream', stream_name)

class Stream(ndb.Model):
    name = ndb.StringProperty()
    number_of_views = ndb.IntegerProperty()
    cover = ndb.BlobProperty()

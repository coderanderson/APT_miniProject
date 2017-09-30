from google.appengine.ext import ndb
from Stream import Stream

class Photo(ndb.Model):
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    data = ndb.BlobProperty()
    stream = ndb.StructuredProperty(Stream)

from google.appengine.ext import ndb

class Photo(ndb.Model):
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    data = ndb.BlobProperty()
    stream = ndb.KeyProperty(kind='Stream')

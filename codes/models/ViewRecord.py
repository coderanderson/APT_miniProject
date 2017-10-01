from google.appengine.ext import ndb
from Stream import Stream

class ViewRecord(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True)
    stream = db.ReferenceProperty(Stream, collection_name='view_records')

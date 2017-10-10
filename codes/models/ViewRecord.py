from google.appengine.ext import ndb


class ViewRecord(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True)
    stream = ndb.KeyProperty(kind='Stream')

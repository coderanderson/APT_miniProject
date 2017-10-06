from google.appengine.ext import ndb
import codes

class User(ndb.Model):
    email = ndb.StringProperty()
    subscription_list = ndb.KeyProperty(kind='Stream', repeated=True)

    @property
    def owned_streams(self):
        return codes.models.Stream.gql("WHERE owner = :1", self.key)


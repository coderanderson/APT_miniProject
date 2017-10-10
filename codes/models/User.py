from google.appengine.ext import ndb
import codes


class User(ndb.Model):
    email = ndb.StringProperty()
    subscription_list = ndb.KeyProperty(kind='Stream', repeated=True)
    getting_trendings = ndb.BooleanProperty()
    trendings_interval = ndb.IntegerProperty()
    last_trending_sent = ndb.DateTimeProperty()

    @property
    def owned_streams(self):
        return codes.models.Stream.gql("WHERE owner = :1", self.key)

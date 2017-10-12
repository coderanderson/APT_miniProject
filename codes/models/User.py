from google.appengine.ext import ndb
import datetime
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

    @classmethod
    def update_trending_preferences(cls, user_email, duration):
        user = User.query().filter(User.email == user_email).get()
        if duration is 0:
            user.getting_trendings = False
        else:
            user.getting_trendings = True
            user.trendings_interval = duration
            user.last_trending_sent = datetime.datetime.now()
        user.put()


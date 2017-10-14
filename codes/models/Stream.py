from google.appengine.ext import ndb
import datetime
import time
import math
import operator

import codes

from google.appengine.api import search

DEFAULT_STREAM_NAME = 'default_stream'
DEFAULT_STREAM_COVER_URL = '/static_files/img/no_cover.png'

STREAM_INDEX = 'stream_index'

class Stream(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    cover_url = ndb.StringProperty()
    tags = ndb.TextProperty()
    owner = ndb.KeyProperty(kind='User')

    @property
    def photos(self):
        return codes.models.Photo.gql("WHERE stream = :1", self.key)
    @property
    def members(self):
        return codes.models.User.gql("WHERE subscription_list = :1", self.key)
    @property
    def view_records(self):
        return codes.models.ViewRecord.gql("WHERE stream = :1", self.key)

    @classmethod
    def remove_old_view_records(cls, duration=3600):
        bound = datetime.datetime.now() - datetime.timedelta(0, duration)
        keys = [ v.key for v in codes.models.ViewRecord.query().filter(codes.models.ViewRecord.date < bound).fetch() ]
        for k in keys:
            k.delete()

    @classmethod
    def create(cls, stream_name, current_user_email, cover_url, message, invitee_emails, host, tags):
        stream_name = stream_name.strip()
        stream = Stream.query().filter(Stream.name == stream_name).get()

        if stream:
            return {'error': 'duplicate stream name'}
        elif stream_name == '':
            return {'error': 'bad stream name'}
        else:
            user = codes.models.User.query().filter(codes.models.User.email == current_user_email).get()
            stream = Stream()
            if cover_url:
                stream.cover_url = cover_url
            stream.name = stream_name
            stream.owner = user.key
            stream.tags = tags
            stream.put()
            user.subscription_list.append(stream.key)
            user.put()
            stream.owner = user.key
            stream.put()
            cls.add_stream_to_index(stream)

            codes.mailers.Mailer.send_invitation_emails(host, stream_name, message, current_user_email, invitee_emails)
            return {}

    @classmethod
    def view(cls, stream_name, page, per_page, All=False):
        stream = Stream.query().filter(Stream.name == stream_name).get()
        if not stream:
            return None

        total_pages = int(math.ceil(stream.photos.count()*1.0/per_page))
        photos = []
        if All:
            photos = stream.photos.order(-codes.models.Photo.creation_date).fetch()
        else:
            photos = stream.photos.order(-codes.models.Photo.creation_date).fetch(per_page, offset=per_page * (page - 1))
        photo_urls = [codes.controllers.view.PhotoViewController.PhotoViewController.generate_url_of_photo(p) for p in photos]
        photo_dates = [p.creation_date for p in photos]

        vr = codes.models.ViewRecord(stream = stream.key)
        vr.put()

        cover_url = stream.cover_url
        if not cover_url:
            cover_url = DEFAULT_STREAM_COVER_URL

        stream.put()

        result = {'stream_name': stream_name,\
                'cover_url': cover_url,\
                'total_pages': total_pages,\
                'page': page,\
                'per_page': per_page,\
                'photo_dates': photo_dates,\
                'photo_urls': photo_urls}
        return result

    @classmethod
    def add_stream_to_index(cls, stream):
        document = search.Document(\
            doc_id = stream.key.urlsafe(),\
            fields = [\
                search.TextField(name='name', value=stream.name),\
                search.TextField(name='tags', value=stream.tags),\
            ])
        index = search.Index(STREAM_INDEX)
        index.put(document)

    @classmethod
    def remove_stream_from_index(cls, stream):
        index = search.Index(STREAM_INDEX)
        document = index.get(stream.key.urlsafe())
        index.delete([document.doc_id])

    @classmethod
    def get_streams_matching_string(cls, query):
        index = search.Index(STREAM_INDEX)
        documents = index.search(query)
        streams=[]
        for d in documents:
            s_key = ndb.Key(urlsafe = d.doc_id)
            s = s_key.get()
            if s:
                streams.append(s)
        return streams

    @classmethod
    def all_streams_matching(cls, query):
        streams = []
        if query:
            streams = cls.get_streams_matching_string(query)
        else:
            streams = Stream.query().fetch()
        result = []
        for s in streams:
            cover_url=s.cover_url
            if not cover_url:
                cover_url = DEFAULT_STREAM_COVER_URL
            result.append({'name': s.name, 'cover_url': cover_url})
        return result

    @classmethod
    def get_top_trending_streams_now(cls, duration_s):
        streams = Stream.query().fetch()
        freq = {}
        bound = datetime.datetime.now() - datetime.timedelta(0, duration_s)
        for s in streams:
            c = s.view_records.filter(codes.models.ViewRecord.date > bound).count()
            cover_url = s.cover_url
            if not cover_url:
                cover_url = DEFAULT_STREAM_COVER_URL
            freq[s.name] = (c, cover_url)
        series = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
        result=[]
        for s in series:
            element = {}
            element['name']=s[0]
            element['count']=s[1][0]
            element['cover_url']=s[1][1]
            result.append(element)
        return result

    @classmethod
    def generate_trending_report(cls, host, stream_view_route):
        duration = 60*60
        series = Stream.get_top_trending_streams_now(duration)[:3]
        stream_names = [ s['name'] for s in series ]
        recipients = []
        now = datetime.datetime.now()
        for user in codes.models.User.query().fetch():
            if user.getting_trendings:
                if user.last_trending_sent + datetime.timedelta(0, user.trendings_interval) < now :
                    recipients.append(user.email)
                    user.last_trending_sent = now
                    user.put()
        codes.mailers.Mailer.send_trending_report_emails(host, stream_view_route, stream_names, recipients)
        for ts in TrendingStream.query().fetch():
            ts.key.delete()
        for s in series:
            ts = TrendingStream()
            ts.name = s['name']
            ts.cover_url = s['cover_url']
            ts.count = s['count']
            ts.put()

    @classmethod
    def bulk_remove_unsubscribe(cls, remove_list, unsubscribe_list, user_email):
        for rname in remove_list:
            stream = Stream.query().filter(Stream.name == rname).get()
            if not stream:
                continue
            key = stream.key
            # TODO: remove all images not only subscribers
            if stream.owner.get().email == user_email:
                for u in stream.members.fetch():
                    u.subscription_list.remove(key)
                    u.put()
                key.delete()
            cls.remove_stream_from_index(stream)
        user = codes.models.User.query().filter(codes.models.User.email == user_email).get()
        for unname in unsubscribe_list:
            stream = Stream.query().filter(Stream.name == unname).get()
            key = stream.key
            if key in user.subscription_list:
                user.subscription_list.remove(key)
            user.put()

    @classmethod
    def get_related_streams_of_user(cls, user_email):
        def get_stream_data(stream):
            name = stream.name
            number_of_photos = stream.photos.count()
            last_new_photo_date = ''
            if number_of_photos > 0:
                last_new_photo_date = stream.photos.order(- codes.models.Photo.creation_date).get().creation_date
                last_new_photo_date = str(last_new_photo_date)
            else:
                last_new_photo_date = time.strftime('%m/%d/%Y', time.gmtime(0))

            return {'name':name, 'number_of_photos':number_of_photos,\
                    'number_of_views':stream.view_records.count(), 'last_new_photo_date':last_new_photo_date}

        user = codes.models.User.query().filter(codes.models.User.email == user_email).get()
        owned_streams = [ get_stream_data(s) for s in user.owned_streams.fetch() if s]
        subscribed_streams = [ get_stream_data(k.get()) for k in user.subscription_list if s]

        return { 'owned_streams': owned_streams, 'subscribed_streams': subscribed_streams }

    @classmethod
    def add_user_to_stream(cls, stream_name, user_email):
        stream = Stream.query().filter(Stream.name == stream_name).get()
        user = codes.models.User.query().filter(codes.models.User.email == user_email).get()
        if stream:
            if not stream.key in user.subscription_list:
                user.subscription_list.append(stream.key)
                user.put()
            return True
        else:
            return False

class TrendingStream(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    cover_url = ndb.StringProperty()
    count = ndb.IntegerProperty()

    @classmethod
    def get_current_trending_streams(cls, user_email):
        streams = TrendingStream.query().fetch()
        streams.sort(key=lambda x: x.count, reverse=True)
        (covers, names, counts)  = ([],[],[])
        for s in streams:
            cover_url=s.cover_url
            if not cover_url:
                cover_url = DEFAULT_STREAM_COVER_URL
            covers.append(s.cover_url)
            names.append(s.name)
            counts.append(s.count)

        duration = 0
        if user_email:
            user = codes.models.User.query().filter(codes.models.User.email == user_email).get()
            if user.getting_trendings:
                duration = user.trendings_interval
        result = {'names': names, 'covers':covers, 'counts': counts, 'duration': duration}
        return result

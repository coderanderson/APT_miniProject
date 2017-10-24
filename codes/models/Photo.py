from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import search
import geopy.distance

import codes

PHOTO_INDEX = 'photo_index'

class Photo(ndb.Model):
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    blob_key = ndb.BlobKeyProperty()
    location = ndb.GeoPtProperty()
    stream = ndb.KeyProperty(kind='Stream')

    @classmethod
    def store(cls, stream_name, uploads, lat=0, lon=0):
        stream = codes.models.Stream.query().filter(codes.models.Stream.name == stream_name).get()
        if not stream:
            return {'error': 'stream not found'}
        photo = Photo(stream = stream.key, location=ndb.GeoPt(lat, lon))
        photo.blob_key = (uploads[0]).key()
        photo.put()
        cls.add_photo_to_index(photo)
        return {}

    @classmethod
    def _pre_delete_hook(cls, key):
        p = key.get()
        blobstore.delete(p.blob_key)
        cls.remove_photo_from_index(p)

    @classmethod
    def add_photo_to_index(cls, photo):
        document = search.Document(\
            doc_id = photo.key.urlsafe(),\
            fields = [\
                search.GeoField(name='location',\
                    value=search.GeoPoint(photo.location.lat, photo.location.lon))
            ])
        index = search.Index(PHOTO_INDEX)
        index.put(document)

    @classmethod
    def remove_photo_from_index(cls, photo):
        index = search.Index(PHOTO_INDEX)
        document = index.get(photo.key.urlsafe())
        index.delete([document.doc_id])

    @classmethod
    def get_nearby_photos(cls, lat, lon, All, number_of_results):
        index = search.Index(PHOTO_INDEX)

        sortexpr = search.SortExpression(\
            expression=("distance(location, geopoint(%f, %f))" % (lat, lon)),\
            direction=search.SortExpression.ASCENDING)
        search_sort_options = search.SortOptions(expressions = [sortexpr])
        search_options = ''
        query = 'distance(location, geopoint(0, 0)) >= 0' # trivial
        if All:
            search_options = search.QueryOptions(sort_options = search_sort_options)
        else:
            search_options = search.QueryOptions( limit = number_of_results,\
                    sort_options = search_sort_options)

        search_query = search.Query(query_string=query, options = search_options)
        documents = index.search(search_query)
        result = []
        for d in documents:
            p_key = ndb.Key(urlsafe = d.doc_id)
            p = p_key.get()
            if p:
                distance = -1
                if p.location:
                    distance = geopy.distance.vincenty((p.location.lat, p.location.lon),\
                            (lat, lon)).ft
                result.append({'key':p.key, 'distance_ft':distance})
        return result

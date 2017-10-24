from google.appengine.ext import ndb
from google.appengine.ext import blobstore
import codes


class Photo(ndb.Model):
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    blob_key = ndb.BlobKeyProperty()
    stream = ndb.KeyProperty(kind='Stream')

    @classmethod
    def store(cls, stream_name, uploads):
        stream = codes.models.Stream.query().filter(codes.models.Stream.name == stream_name).get()
        if not stream:
            return {'error': 'stream not found'}
        photo = Photo(stream = stream.key)
        photo.blob_key = (uploads[0]).key()
        photo.put()
        return {}

    @classmethod
    def _pre_delete_hook(cls, key):
        p = key.get()
        blobstore.delete(p.blob_key)

import webapp2
import urllib
from codes.models import *
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore

class PhotoViewController(blobstore_handlers.BlobstoreDownloadHandler):
    view_route = '/get_photo'

    @classmethod
    def generate_url_of_photo(cls, p):
        query_params = {'img_id': p.key.urlsafe()}
        return cls.view_route + '?' + urllib.urlencode(query_params)

    def view(self):
        try:
            photo_key = ndb.Key(urlsafe=self.request.get('img_id'))
            photo = photo_key.get()
            if photo:
                self.response.headers['Content-Type'] = 'image/png'
                self.send_blob(photo.blob_key)
            else:
                self.error(404)
        except:
            self.error(404)

class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    upload_raw_url = '/send_photo'
    upload_url = blobstore.create_upload_url(upload_raw_url)
    def post(self):
        stream_name = self.request.get('stream_name', DEFAULT_STREAM_NAME)

        result = Photo.store(stream_name, self.get_uploads())
        if 'error' in result:
            self.response.set_status(404)
            self.response.out.write(json.dumps({'error': result['error']}))
        else:
            query_params = {'stream_name': stream_name, 'All':0}
            self.redirect('/view_stream?' + urllib.urlencode(query_params))

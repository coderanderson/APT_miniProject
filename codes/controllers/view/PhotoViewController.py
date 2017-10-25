import webapp2
import urllib
import json
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
        lat = float(self.request.get('lat', 0))
        lon = float(self.request.get('lon', 0))
        #lat, lon = 0,0
        result = Photo.store(stream_name, self.get_uploads(), lat, lon)

        PhotoUploadHandler.upload_url = blobstore.create_upload_url(PhotoUploadHandler.upload_raw_url)
        self.response.headers['Content-Type'] = 'application/json'

        if 'error' in result:
            self.response.set_status(404)
            self.response.out.write(json.dumps({'error': result['error']}))
        else:
            response = json.dumps({'description': 'send the request to the new_url',\
                'new_url': PhotoUploadHandler.upload_url})
            self.response.out.write(response)


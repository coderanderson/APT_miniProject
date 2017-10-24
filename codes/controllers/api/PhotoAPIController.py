import webapp2
import urllib
import json
from codes.models import *
from google.appengine.ext import ndb
from codes.controllers.view.PhotoViewController import PhotoUploadHandler
from codes.controllers.view.PhotoViewController import PhotoViewController

class PhotoAPIController(webapp2.RequestHandler):
    def create(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.set_status(302)
        self.response.out.write(json.dumps({'description': 'send the request to the new_url',\
            'new_url': PhotoUploadHandler.upload_url}))

    location_search_api_url = '/api/nearby_photo'
    def nearby_photo_search(self):
        lat = float(self.request.get('lat', 0))
        lon = float(self.request.get('lon', 0))
        All = int(self.request.get('All', 0))
        per_page = int(self.request.get('per_page', 16))

        photos = Photo.get_nearby_photos(lat, lon, All==1, per_page)
        result = {'photos': []}
        for o in photos:
            pk = o['key']
            p = pk.get()
            distance_ft = o['distance_ft']
            purl = PhotoViewController.generate_url_of_photo(p)
            stream_name = p.stream.get().name
            result['photos'].append({'url': purl,\
                    'stream_name': stream_name,\
                    'distance_ft': distance_ft})

        self.response.headers['Content-Type'] = 'application/json'
        self.response.set_status(200)
        self.response.out.write(json.dumps(result))

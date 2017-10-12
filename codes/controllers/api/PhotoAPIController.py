import webapp2
import urllib
import json
from codes.models import *
from google.appengine.ext import ndb
from codes.controllers.view.PhotoViewController import PhotoUploadHandler

class PhotoAPIController(webapp2.RequestHandler):
    def create(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.set_status(302)
        self.response.out.write(json.dumps({'description': 'send the request to the new_url',\
            'new_url': PhotoUploadHandler.upload_url}))

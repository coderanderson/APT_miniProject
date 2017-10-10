import jinja2
import os

debug = True

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/codes/views'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

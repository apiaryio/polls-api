from rivr.wsgi import WSGIHandler
from polls.app import app

wsgi = WSGIHandler(app)


# rest api 

from flask import Flask
from . import admin, user

app_name = 'Event_tracker'


def get_app():
	app = Flask(app_name)
	app.register_blueprint(admin.blueprint)
	app.register_blueprint(user.blueprint)
	return app
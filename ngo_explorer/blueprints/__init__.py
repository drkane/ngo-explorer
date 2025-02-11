from flask import Flask

from ngo_explorer.blueprints.data import bp as data
from ngo_explorer.blueprints.home import bp as home
from ngo_explorer.blueprints.upload import bp as upload


def add_blueprints(app: Flask):
    app.register_blueprint(home)
    app.register_blueprint(data)
    app.register_blueprint(upload)

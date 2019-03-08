from .home import bp as home
from .data import bp as data
from .upload import bp as upload

def add_blueprints(app):
    app.register_blueprint(home)
    app.register_blueprint(data)
    app.register_blueprint(upload)

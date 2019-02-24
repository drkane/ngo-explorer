import os

from flask import Flask
from slugify import slugify
import requests_cache

from .blueprints import home, data
from .utils.charts import location_map, plotly_json
from .utils.utils import update_url_values

def create_app(test_config=None):
    
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        PLOTLY_GEO_SCOPES=['europe', 'asia',
                           'africa', 'north america', 'south america'],
        CHARITYBASE_API_KEY=os.environ.get("CHARITYBASE_API_KEY")
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # set up url caching
    # @TODO set to a redis instance for live version
    one_week = 60 * 60 * 24 * 7 # in seconds
    requests_cache.install_cache('demo_cache', expire_after=one_week, allowable_methods=('GET', 'POST'))

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(home.bp)
    app.register_blueprint(data.bp)

    # register template filters
    @app.template_filter('slugify')
    def template_slugify(s):
        return slugify(s)

    @app.template_filter('location_map')
    def template_location_map(countries, **kwargs):
        return location_map(countries, **kwargs)

    @app.template_filter('to_plotlyjson')
    def template_to_plotlyjson(data: dict):
        return plotly_json(data)

    @app.template_filter('update_url')
    def template_update_url_values(url: str, values: dict):
        return update_url_values(url, values)

    return app

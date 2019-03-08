import os
import random

from flask import Flask
from slugify import slugify
import requests_cache
import click

from .commands.countries import update_countries
from .blueprints import home, data, upload
from .utils.charts import location_map, plotly_json
from .utils.utils import update_url_values, correct_titlecase, scale_value
from .utils.filters import CLASSIFICATION, REGIONS
from .utils.download import DOWNLOAD_OPTIONS
from .utils.countries import SIMILAR_INITIATIVE, get_country_groups

def create_app(test_config=None):
    
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        PLOTLY_GEO_SCOPES=['europe', 'asia',
                           'africa', 'north america', 'south america'],
        CHARITYBASE_API_KEY=os.environ.get("CHARITYBASE_API_KEY"),
        DATA_CONTAINER=os.environ.get(
            "DATA_CONTAINER",
            os.path.join(os.getcwd(), "uploads")
        ),
        DOWNLOAD_LIMIT=500,
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
    requests_cache.install_cache(
        os.path.join(app.config["DATA_CONTAINER"], 'demo_cache'),
        expire_after=one_week,
        allowable_methods=('GET', 'POST')
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(home.bp)
    app.register_blueprint(data.bp)
    app.register_blueprint(upload.bp)

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

    @app.template_filter('correct_titlecase')
    def template_correct_titlecase(s: str):
        return correct_titlecase(s)

    @app.template_filter('number_format')
    def template_number_format(v: (int, float)):
        return scale_value(v, True)

    @app.template_filter('randomn')
    def template_randomn(seq, n=1):
        return random.sample(seq, min((n, len(seq))))

    # add custom context to templates
    @app.context_processor
    def inject_context_vars():
        return dict(
            classification=CLASSIFICATION,
            regions=REGIONS,
            download_options=DOWNLOAD_OPTIONS,
            similar_initiative=SIMILAR_INITIATIVE,
            countries=get_country_groups(),
        )

    # add custom commands
    @app.cli.command('update-countries')
    def cli_update_countries():
        update_countries()

    return app

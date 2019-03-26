from datetime import datetime
import os
import random

from flask import Flask, request
from flask_babel import Babel
from babel.numbers import format_decimal
from slugify import slugify
import requests_cache

from .commands import add_custom_commands
from .blueprints import add_blueprints
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
        CHARITYBASE_URL='https://charitybase.uk/api/graphql',
        DATA_CONTAINER=os.environ.get(
            "DATA_CONTAINER",
            os.path.join(os.getcwd(), "uploads")
        ),
        DOWNLOAD_LIMIT=500,
        LANGUAGES=['en'],
        BABEL_TRANSLATION_DIRECTORIES='../translations',
        REQUEST_CACHE_BACKEND='sqlite',
    )
    app.config["REQUEST_CACHE_LOCATION"] = os.path.join(
        app.config["DATA_CONTAINER"], 'demo_cache')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # add translation
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config['LANGUAGES'])

    # set up url caching
    # @TODO set to a redis instance for live version
    one_week = 60 * 60 * 24 * 7 # in seconds
    requests_cache.install_cache(
        app.config["REQUEST_CACHE_LOCATION"],
        backend=app.config["REQUEST_CACHE_BACKEND"],
        expire_after=one_week,
        allowable_methods=('GET', 'POST'),
        include_get_headers=True,
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    add_blueprints(app)
    add_context_processors(app)
    add_template_filters(app)
    add_custom_commands(app)

    return app


def add_template_filters(app):
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
    def template_correct_titlecase(s: str, **kwargs):
        return correct_titlecase(s, **kwargs)

    @app.template_filter('number_format')
    def template_number_format(v: (int, float)):
        return scale_value(v, True)

    @app.template_filter('_n')
    def template_babel_number_format(v: (int, float)):
        if v:
            return format_decimal(v)
        return v

    @app.template_filter('randomn')
    def template_randomn(seq, n=1):
        return random.sample(seq, min((n, len(seq))))

    @app.template_filter('first_upper')
    def template_randomn(s: str):
        return s[0].upper() + s[1:]


def add_context_processors(app):
    # add custom context to templates
    @app.context_processor
    def inject_context_vars():
        return dict(
            classification=CLASSIFICATION,
            regions=REGIONS,
            download_options=DOWNLOAD_OPTIONS,
            similar_initiative=SIMILAR_INITIATIVE,
            countries=get_country_groups(),
            now=datetime.now(),
        )

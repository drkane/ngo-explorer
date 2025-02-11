import os
import random
from datetime import datetime
from typing import Optional, Union

import requests_cache
from babel.numbers import format_decimal
from flask import Flask, request
from flask_babel import Babel
from slugify import slugify

from ngo_explorer.blueprints import add_blueprints
from ngo_explorer.commands import add_custom_commands
from ngo_explorer.utils.charts import location_map, plotly_json
from ngo_explorer.utils.countries import SIMILAR_INITIATIVE, get_country_groups
from ngo_explorer.utils.download import DOWNLOAD_OPTIONS
from ngo_explorer.utils.filters import CLASSIFICATION, REGIONS
from ngo_explorer.utils.utils import correct_titlecase, scale_value, update_url_values


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        PLOTLY_GEO_SCOPES=[
            "europe",
            "asia",
            "africa",
            "north america",
            "south america",
        ],
        GA_TRACKING_ID=os.environ.get("GA_TRACKING_ID"),
        FTC_DB_URL=os.environ.get("FTC_DB_URL"),
        DB_LOCATION=os.environ.get("DB_LOCATION", "charitydata.sqlite"),
        DATA_CONTAINER=os.environ.get(
            "DATA_CONTAINER", os.path.join(os.getcwd(), "uploads")
        ),
        DOWNLOAD_LIMIT=int(os.environ.get("DOWNLOAD_LIMIT", 500)),
        LANGUAGES=["en"],
        BABEL_TRANSLATION_DIRECTORIES="../translations",
        BABEL_DEFAULT_LOCALE="en",
        REQUEST_CACHE_BACKEND="sqlite",
    )
    app.config["REQUEST_CACHE_LOCATION"] = os.path.join(
        app.config["DATA_CONTAINER"], "demo_cache"
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    def get_locale():
        return request.accept_languages.best_match(app.config["LANGUAGES"])

    # add translation
    Babel(app, locale_selector=get_locale)

    # set up url caching
    # @TODO set to a redis instance for live version
    one_week = 60 * 60 * 24 * 7  # in seconds
    requests_cache.install_cache(
        app.config["REQUEST_CACHE_LOCATION"],
        backend=app.config["REQUEST_CACHE_BACKEND"],
        expire_after=one_week,
        allowable_methods=("GET", "POST"),
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


def add_template_filters(app: Flask):
    # register template filters
    @app.template_filter("slugify")
    def template_slugify(s: str) -> str:
        return slugify(s)

    @app.template_filter("location_map")
    def template_location_map(countries, **kwargs):
        return location_map(countries, **kwargs)

    @app.template_filter("to_plotlyjson")
    def template_to_plotlyjson(data: dict):
        return plotly_json(data)

    @app.template_filter("update_url")
    def template_update_url_values(url: str, values: dict) -> str:
        return update_url_values(url, values)

    @app.template_filter("correct_titlecase")
    def template_correct_titlecase(s: str, **kwargs) -> str:
        return correct_titlecase(s, **kwargs)

    @app.template_filter("number_format")
    def template_number_format(v: Union[int, float]):
        return scale_value(v, True)

    @app.template_filter("_n")
    def template_babel_number_format(v: Optional[int | float], format: str = "#,##0"):
        if v:
            return format_decimal(v, format=format)
        return v

    @app.template_filter("randomn")
    def template_randomn(seq, n=1):
        return random.sample(seq, min((n, len(seq))))

    @app.template_filter("first_upper")
    def template_first_upper(s: str) -> str:
        return s[0].upper() + s[1:]


def add_context_processors(app: Flask):
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

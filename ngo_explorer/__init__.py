import os
import random
from datetime import datetime
from typing import Optional, Union

import requests_cache
import sentry_sdk
from babel.numbers import format_decimal
from flask import Flask, request
from flask_babel import Babel
from slugify import slugify

from ngo_explorer import settings
from ngo_explorer.blueprints import add_blueprints
from ngo_explorer.commands import add_custom_commands
from ngo_explorer.db import close_connection
from ngo_explorer.utils.charts import location_map, plotly_json
from ngo_explorer.utils.countries import SIMILAR_INITIATIVE, get_country_groups
from ngo_explorer.utils.download import DOWNLOAD_OPTIONS
from ngo_explorer.utils.fetchdata import fetch_all_charities
from ngo_explorer.utils.filters import CLASSIFICATION, REGIONS
from ngo_explorer.utils.utils import (
    correct_titlecase,
    scale_value,
    to_titlecase,
    update_url_values,
)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=settings.SECRET_KEY,
        PLOTLY_GEO_SCOPES=settings.PLOTLY_GEO_SCOPES,
        GA_TRACKING_ID=settings.GA_TRACKING_ID,
        FTC_DB_URL=settings.FTC_DB_URL,
        DATA_CONTAINER=settings.DATA_CONTAINER,
        DB_LOCATION=settings.DB_LOCATION,
        DOWNLOAD_LIMIT=settings.DOWNLOAD_LIMIT,
        LANGUAGES=settings.LANGUAGES,
        BABEL_TRANSLATION_DIRECTORIES=settings.BABEL_TRANSLATION_DIRECTORIES,
        BABEL_DEFAULT_LOCALE=settings.BABEL_DEFAULT_LOCALE,
        REQUEST_CACHE_BACKEND=settings.REQUEST_CACHE_BACKEND,
        REQUEST_CACHE_LOCATION=settings.REQUEST_CACHE_LOCATION,
        SENTRY_DSN=settings.SENTRY_DSN,
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

    if app.config["SENTRY_DSN"]:
        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            send_default_pii=True,
            traces_sample_rate=0.1,
            profile_session_sample_rate=0.1,
            profile_lifecycle="trace",
            enable_logs=True,
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

    @app.teardown_appcontext
    def close_db_connection(e=None):
        close_connection(e)

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

    @app.template_filter("to_titlecase")
    def template_to_titlecase(s: str | None, sentence: bool = False) -> str | None:
        return to_titlecase(s, sentence=sentence)

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
            all_charity_data=fetch_all_charities(),
        )

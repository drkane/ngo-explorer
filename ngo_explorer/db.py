import logging
from datetime import datetime, timedelta

from flask import current_app, g
from sqlite_utils import Database

logger = logging.getLogger(__name__)

ONE_DAY_AGO = timedelta(days=1)


def get_db() -> Database:
    now = datetime.now()
    db = getattr(g, "_database", None)
    last_updated = getattr(g, "_last_updated", now)
    if db is None or last_updated < (now - ONE_DAY_AGO):
        db = g._database = Database(
            current_app.config["DB_LOCATION"], tracer=logger.info
        )
        g._last_updated = now
    return db


def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

from flask import current_app, g
from sqlite_utils import Database

DATABASE = "/path/to/database.db"


def get_db() -> Database:
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = Database(current_app.config["DB_LOCATION"], tracer=print)
    return db


def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

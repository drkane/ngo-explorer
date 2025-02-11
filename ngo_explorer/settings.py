import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
PLOTLY_GEO_SCOPES = [
    "europe",
    "asia",
    "africa",
    "north america",
    "south america",
]
GA_TRACKING_ID = os.environ.get("GA_TRACKING_ID")
FTC_DB_URL = os.environ.get("FTC_DB_URL")
DATA_CONTAINER = os.environ.get("DATA_CONTAINER", os.path.join(os.getcwd(), "uploads"))
DB_LOCATION = os.environ.get(
    "DB_LOCATION", os.path.join(DATA_CONTAINER, "charitydata.sqlite")
)
DOWNLOAD_LIMIT = int(os.environ.get("DOWNLOAD_LIMIT", 500))
LANGUAGES = ["en"]
BABEL_TRANSLATION_DIRECTORIES = "../translations"
BABEL_DEFAULT_LOCALE = "en"
REQUEST_CACHE_BACKEND = "sqlite"
REQUEST_CACHE_LOCATION = os.path.join(DATA_CONTAINER, "demo_cache")

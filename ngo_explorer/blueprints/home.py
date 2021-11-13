from flask import Blueprint, render_template

from ..utils.countries import get_country_groups
from ..utils.filters import CLASSIFICATION

bp = Blueprint("home", __name__, url_prefix="/")


@bp.route("/")
def index():
    return render_template("index.html.j2")


@bp.route("/about")
def about():
    return render_template("about.html.j2")

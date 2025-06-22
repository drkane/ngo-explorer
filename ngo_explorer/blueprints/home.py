from flask import Blueprint, render_template

bp = Blueprint("home", __name__, url_prefix="/")


@bp.route("/")
def index():
    return render_template("index.html.j2")


@bp.route("/about")
def about():
    return render_template("about.html.j2")

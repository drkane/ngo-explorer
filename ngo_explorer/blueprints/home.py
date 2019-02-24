from flask import Blueprint, render_template

from ..utils.countries import get_country_groups

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('index.html.j2', countries=get_country_groups())


@bp.route('/about')
def about():
    return render_template('index.html.j2')


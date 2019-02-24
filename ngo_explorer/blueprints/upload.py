import re
import uuid
import pickle
import os

from flask import Blueprint, render_template, request, jsonify, url_for, redirect, current_app

from ..utils.fetchdata import fetch_charitybase_fromids
from ..utils.charts import get_charts

bp = Blueprint('upload', __name__, url_prefix='/upload')

@bp.route('/')
def data():
    return render_template('upload.html.j2')

@bp.route('/', methods=['POST'])
def process_data():
    charitynumbers = request.values.get("charitynumbers")
    if not charitynumbers:
        return None

    charitynumbers = re.split(r'\W+', charitynumbers)
    charitynumbers = set(charitynumbers)
    charitynumbers = sorted([c.strip() for c in charitynumbers])

    charity_data = fetch_charitybase_fromids(charitynumbers)
    charts = get_charts(charity_data)

    list_id = str(uuid.uuid4())

    # @TODO: save list here using list ID
    with open(os.path.join(current_app.config["DATA_CONTAINER"], "{}.pkl".format(list_id)), "wb") as a:
        pickle.dump(dict(
            charitynumbers=charitynumbers,
            data=charity_data,
            charts=charts
        ), a)

    return redirect(url_for('.fetch_uploaded_data', fileid=list_id), code=303)

@bp.route('/<fileid>')
def fetch_uploaded_data(fileid):

    with open(os.path.join(current_app.config["DATA_CONTAINER"], "{}.pkl".format(fileid)), "rb") as a:
        data = pickle.load(a)

    return render_template('upload-data.html.j2', **data)

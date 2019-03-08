import re
import uuid
import pickle
import os

from flask import Blueprint, render_template, request, jsonify, url_for, redirect, current_app

from ..utils.fetchdata import fetch_charitybase
from ..utils.download import DOWNLOAD_OPTIONS, download_file
from ..utils.filters import parse_filters

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

    charity_data = fetch_charitybase(ids=charitynumbers)

    list_id = str(uuid.uuid4())

    title = request.values.get("upload-name")

    with open(os.path.join(current_app.config["DATA_CONTAINER"], "{}.pkl".format(list_id)), "wb") as a:
        pickle.dump(dict(
            title=title,
            charitynumbers=charitynumbers,
            data=charity_data,
        ), a)

    return redirect(url_for('.fetch_uploaded_data', fileid=list_id), code=303)


def upload_pages(fileid):
    return {
        "dashboard": {
            "name": "Dashboard",
            "url": url_for('.fetch_uploaded_data', fileid=fileid),
        },
        "show-charities": {
            "name": "Show NGOs",
            "url": url_for('.list_uploaded_data', fileid=fileid),
        },
        "download": {
            "name": "Download",
            "url": url_for('.download_uploaded_data', fileid=fileid),
        },
    }

@bp.route('/<fileid>')
def fetch_uploaded_data(fileid):

    with open(os.path.join(current_app.config["DATA_CONTAINER"], "{}.pkl".format(fileid)), "rb") as a:
        data = pickle.load(a)
    data["data"].set_charts()
    return render_template('upload-data.html.j2', pages=upload_pages(fileid), **data)

@bp.route('/<fileid>/show')
def list_uploaded_data(fileid):

    with open(os.path.join(current_app.config["DATA_CONTAINER"], "{}.pkl".format(fileid)), "rb") as a:
        data = pickle.load(a)

    filters = parse_filters(request.values)
    if filters.get("skip", 0) > 0:
        data["data"] = fetch_charitybase(
            ids=data["charitynumbers"], filters={}, limit=30, skip=filters.get("skip", 0), query="charity_list")

    return render_template('upload-data-show-charities.html.j2', pages=upload_pages(fileid), filters=request.values, charts={}, **data)

@bp.route('/<fileid>/download', methods=['GET', 'POST'])
def download_uploaded_data(fileid):

    with open(os.path.join(current_app.config["DATA_CONTAINER"], "{}.pkl".format(fileid)), "rb") as a:
        data = pickle.load(a)

    if "download_type" in request.values:
        return download_file(
            area={"name": data["title"], "ids": data["charitynumbers"]},
            filters={},
            fields=request.values.getlist("fields"),
            filetype=request.values.get("download_type").lower(),
        )

    return render_template('upload-data-download.html.j2', pages=upload_pages(fileid), charts={}, **data)

import os
import pickle
import re
import uuid

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_babel import _

from ..utils.download import DOWNLOAD_OPTIONS, download_file
from ..utils.fetchdata import fetch_charitybase
from ..utils.filters import parse_filters
from .data import data_page

bp = Blueprint("upload", __name__, url_prefix="/upload")


@bp.route("/")
def data():
    return render_template("upload.html.j2")


@bp.route("/", methods=["POST"])
def process_data():
    charitynumbers = request.values.get("charitynumbers")
    if not charitynumbers:
        return None

    charitynumbers = re.split(r"\W+", charitynumbers)
    charitynumbers = set(charitynumbers)
    charitynumbers = sorted([c.strip() for c in charitynumbers])

    # charity_data = fetch_charitybase(ids=charitynumbers)

    list_id = str(uuid.uuid4())

    title = request.values.get("upload-name")

    with open(
        os.path.join(current_app.config["DATA_CONTAINER"], "{}.pkl".format(list_id)),
        "wb",
    ) as a:
        pickle.dump(
            dict(
                title=title,
                charitynumbers=charitynumbers,
                # data=charity_data,
            ),
            a,
        )

    return redirect(url_for(".fetch_uploaded_data", fileid=list_id), code=303)


def upload_pages(fileid):
    return {
        "dashboard": {
            "name": _("Dashboard"),
            "url": url_for(".fetch_uploaded_data", fileid=fileid),
        },
        "show-charities": {
            "name": _("Show NGOs"),
            "url": url_for(".list_uploaded_data", fileid=fileid),
        },
        "download": {
            "name": _("Download"),
            "url": url_for(".download_uploaded_data", fileid=fileid),
        },
    }


@bp.route("/<fileid>/<subpage>.<filetype>", methods=["GET", "POST"])
@bp.route("/<fileid>.<filetype>", methods=["GET", "POST"])
@bp.route("/<fileid>/<subpage>")
@bp.route("/<fileid>")
def fetch_uploaded_data(fileid, filetype="html", subpage="dashboard"):
    if subpage not in ["dashboard", "show-charities", "download"]:
        return render_template("404.html.j2"), 404

    filepath = os.path.join(
        current_app.config["DATA_CONTAINER"], "{}.pkl".format(fileid)
    )

    if not os.path.exists(filepath):
        return (
            render_template(
                "404.html.j2",
                lookingfor=_('File "%(fileid)s" could not be found', fileid=fileid),
            ),
            404,
        )

    with open(filepath, "rb") as a:
        data = pickle.load(a)

    return data_page(
        area={
            "name": data["title"] if data["title"] else "Data upload",
            "type": "upload",
        },
        charity_ids=data["charitynumbers"],
        filetype=filetype,
        page=subpage,
        url_base=["upload.fetch_uploaded_data", {"fileid": fileid}],
    )

    data["data"].set_charts()
    data["all_charity_data"] = fetch_charitybase(query="all_charities")
    return render_template("data.html.j2", pages=upload_pages(fileid), **data)

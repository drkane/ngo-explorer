import os
import pickle
import re
import uuid
from typing import Optional

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_babel import _

from ngo_explorer.blueprints.data import data_page
from ngo_explorer.utils.countries import CountryGroupItemUpload

bp = Blueprint("upload", __name__, url_prefix="/upload")


@bp.route("/")
def data():
    return render_template("upload.html.j2")


@bp.route("/", methods=["POST"])
def process_data():
    charitynumbers_raw: Optional[str] = request.values.get("charitynumbers")
    if not charitynumbers_raw:
        abort(400)

    charitynumbers = re.split(r"\W+", charitynumbers_raw)
    charitynumbers = set(charitynumbers)
    charitynumbers = sorted([c.strip() for c in charitynumbers if isinstance(c, str)])

    # charity_data = fetch_charity_details(ids=charitynumbers)

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
        area=CountryGroupItemUpload(
            name=data["title"] if data["title"] else "Data upload",
            type_="upload",
        ),
        charity_ids=data["charitynumbers"],
        filetype=filetype,
        page=subpage,
        url_base=["upload.fetch_uploaded_data", {"fileid": fileid}],
    )

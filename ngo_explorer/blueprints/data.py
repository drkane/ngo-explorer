from typing import Optional

from flask import Blueprint, Response, jsonify, render_template, request, url_for
from flask_babel import _

from ngo_explorer.classes.charitylookupcharity import CharityLookupCharity
from ngo_explorer.classes.countries import (
    CountryGroupItem,
    CountryGroupItemList,
    CountryGroupItemUpload,
)
from ngo_explorer.utils.countries import (
    get_country_groups_lists,
    get_multiple_countries,
)
from ngo_explorer.utils.download import download_file
from ngo_explorer.utils.fetchdata import (
    fetch_all_charities,
    fetch_charity_details,
    fetch_iati,
    fetch_iati_by_charity,
)
from ngo_explorer.utils.filters import parse_filters

SUBPAGES = ["dashboard", "show-charities", "download"]

bp: Blueprint = Blueprint("data", __name__, url_prefix="/")


@bp.route(
    "/region/<regiontype>/<regionid>/<subpage>.<filetype>", methods=["GET", "POST"]
)
@bp.route("/region/<regiontype>/<regionid>.<filetype>", methods=["GET", "POST"])
@bp.route("/region/<regiontype>/<regionid>/<subpage>")
@bp.route("/region/<regiontype>/<regionid>")
def region(
    regionid: str,
    regiontype: str = "continent",
    filetype: str = "html",
    subpage: str = "dashboard",
) -> tuple[str, int] | str | Response:
    if subpage not in SUBPAGES:
        return render_template("404.html.j2"), 404

    area = get_country_groups_lists().get((regiontype, regionid))

    if not area:
        return (
            render_template(
                "404.html.j2",
                lookingfor=_(
                    '%(regiontype)s "%(regionid)s" could not be found',
                    regiontype=regiontype,
                    regionid=regionid,
                ),
            ),
            404,
        )

    return data_page(
        area,
        filetype=filetype,
        page=subpage,
        url_base=[".region", {"regiontype": regiontype, "regionid": regionid}],
    )


@bp.route("/country/<countryid>/<subpage>.<filetype>", methods=["GET", "POST"])
@bp.route("/country/<countryid>.<filetype>", methods=["GET", "POST"])
@bp.route("/country/<countryid>/<subpage>")
@bp.route("/country/<countryid>")
def country(
    countryid: str, filetype: str = "html", subpage: str = "dashboard"
) -> tuple[str, int] | str | Response:
    if subpage not in SUBPAGES:
        return render_template("404.html.j2"), 404

    area = get_multiple_countries(countryid)

    if not area:
        return (
            render_template(
                "404.html.j2",
                lookingfor=_(
                    'Country "%(countryid)s" could not be found', countryid=countryid
                ),
            ),
            404,
        )

    return data_page(
        area,
        filetype=filetype,
        page=subpage,
        url_base=[".country", {"countryid": countryid}],
    )


def data_page(
    area: Optional[
        CountryGroupItem | CountryGroupItemList | CountryGroupItemUpload
    ] = None,
    charity_ids: Optional[list[str]] = None,
    filetype: str = "html",
    page: str = "dashboard",
    url_base=[],
) -> tuple[str, int] | str | Response:
    if request.method == "POST":
        filters_raw = request.form
    else:
        filters_raw = request.args
    filters_url = {
        k: v if k in ["filter-countries", "filter-classification"] else v[0]
        for k, v in filters_raw.lists()
        if v != [""]
    }

    pages = {
        "dashboard": {
            "name": _("Dashboard"),
            "template": "data.html.j2",
            "url": url_for(url_base[0], **{**url_base[1], **filters_url}),
            "api_url": url_for(
                url_base[0], **{**url_base[1], **filters_url, "filetype": "json"}
            ),
        },
        "show-charities": {
            "name": _("Show NGOs"),
            "template": "data-show-charities.html.j2",
            "url": url_for(
                url_base[0],
                **{**url_base[1], **filters_url, "subpage": "show-charities"},
            ),
            "api_url": url_for(
                url_base[0],
                **{
                    **url_base[1],
                    **filters_url,
                    "subpage": "show-charities",
                    "filetype": "json",
                },
            ),
        },
        "download": {
            "name": _("Download"),
            "template": "data-download.html.j2",
            "url": url_for(
                url_base[0], **{**url_base[1], **filters_url, "subpage": "download"}
            ),
            "api_url": url_for(
                url_base[0],
                **{
                    **url_base[1],
                    **filters_url,
                    "subpage": "download",
                    "filetype": "json",
                },
            ),
        },
    }
    qgl_query = "charity_aggregation" if page == "dashboard" else "charity_list"

    filters = parse_filters(filters_raw)

    download_type = request.values.get("download_type")
    if download_type:
        return download_file(
            area=area,
            ids=charity_ids,
            filters=filters,
            fields=request.values.getlist("fields"),
            filetype=download_type.lower(),
        )

    all_charity_data = fetch_all_charities()
    fetch_countries = None
    fetch_ids = None
    if area and area.countries:
        fetch_countries = area.countries
    if charity_ids:
        fetch_ids = charity_ids

    charity_data = fetch_charity_details(
        filters=filters,
        limit=30,
        skip=getattr(filters, "skip", 0),
        query=qgl_query,
        sort="random" if page == "dashboard" else "default",
        countries=fetch_countries,
        ids=fetch_ids,
    )
    charity_data.set_charts()

    iati_data = None
    if area and area.countries:
        for country in area.countries:
            # whether the country has been filtered to the
            country.filtered = (
                country.id in filters.countries if filters.countries else True
            )
            # number of charities in the selection that work in the country
            if charity_data.aggregate and charity_data.aggregate.areas:
                country.count = sum(
                    [
                        bucket.count
                        for bucket in charity_data.aggregate.areas
                        if bucket.key == country.iso2
                    ]
                )

        iati_data = fetch_iati(area.countries)

    if filetype == "json":
        inserts = {
            "selected-filters": render_template(
                "_data_selected_filters.html.j2", filters=filters_raw, area=area
            ),
            "example-charities": render_template(
                "_data_example_charities.html.j2",
                data=charity_data,
                area=area,
                all_charity_data=all_charity_data,
            ),
            "charity-count": "{:,.0f} UK NGO{}".format(
                charity_data.count, "" if charity_data.count == 1 else "s"
            ),
            "word-cloud": render_template(
                "_data_word_cloud.html.j2", data=charity_data
            ),
            "max-countries-header": "{:,.0f}".format(filters.max_countries),
        }

        if page == "show-charities":
            inserts["data-list"] = render_template(
                "_data_list_table.html.j2",
                pages=pages,
                active_page="show-charities",
                filters=filters_raw,
                data=charity_data,
                area=area,
            )

        return jsonify(
            dict(
                area=area,
                inserts=inserts,
                charts=charity_data.get_charts(),
                filters=filters_raw,
                pages=pages,
            )
        )

    return render_template(
        pages[page]["template"],
        area=area,
        data=charity_data,
        all_charity_data=all_charity_data,
        iati_data=iati_data,
        filters=filters_raw,
        pages=pages,
        region_type=url_base[1].get("regiontype"),
        api_url=pages[page]["api_url"],
    )


@bp.route("/charity/<charityid>")
def charity(charityid: str) -> tuple[str, int] | str | Response:
    charity_data = fetch_charity_details(ids=[charityid], all_finances=True)

    if charity_data.count == 0:
        return (
            render_template(
                "404.html.j2",
                lookingfor=_(
                    'Charity "%(charityid)s" could not be found', charityid=charityid
                ),
            ),
            404,
        )

    char = charity_data.get_charity()
    if not isinstance(char, CharityLookupCharity):
        return (
            render_template(
                "404.html.j2",
                lookingfor=_(
                    'Charity "%(charityid)s" could not be found', charityid=charityid
                ),
            ),
            404,
        )
    char.iati = fetch_iati_by_charity(getattr(char, "orgIds"))

    return render_template("charity.html.j2", data=char)

from flask import Blueprint, render_template, request, jsonify, url_for, Response

from ..utils.countries import get_country_groups, get_multiple_countries, COUNTRIES
from ..utils.fetchdata import fetch_charitybase, fetch_iati, fetch_charitybase_fromids, dict_to_gql
from ..utils.filters import CLASSIFICATION, parse_filters
from ..utils.download import DOWNLOAD_OPTIONS, download_file
from ..utils.charts import get_charts
from ..utils.utils import nested_to_record

bp = Blueprint('data', __name__, url_prefix='/')

SIMILAR_INITIATIVE = {
    "sen": [{
        "homepage": "https://pfongue.org/",
        "title": "Platform of European NGOs in Senegal",
        "directlink": "https://pfongue.org/-Cartographie-.html",
        "directlinktext": "Map of projects",
    }]
}


@bp.route('/region/<regiontype>/<regionid>/<subpage>.<filetype>', methods=['GET', 'POST'])
@bp.route('/region/<regiontype>/<regionid>.<filetype>', methods=['GET', 'POST'])
@bp.route('/region/<regiontype>/<regionid>/<subpage>')
@bp.route('/region/<regiontype>/<regionid>')
def region(regionid, regiontype="continent", filetype="html", subpage="dashboard"):
    area = get_country_groups(as_dict=True).get((regiontype, regionid))
    return data_page(
        area,
        filetype,
        subpage,
        url_base=[".region", {"regiontype": regiontype, "regionid": regionid}]
    )


@bp.route('/country/<countryid>/<subpage>.<filetype>', methods=['GET', 'POST'])
@bp.route('/country/<countryid>.<filetype>', methods=['GET', 'POST'])
@bp.route('/country/<countryid>/<subpage>')
@bp.route('/country/<countryid>')
def country(countryid, filetype="html", subpage='dashboard'):
    area = get_multiple_countries(countryid)
    return data_page(
        area,
        filetype,
        subpage,
        url_base=[".country", {"countryid": countryid}]
    )

def data_page(area, filetype="html", page='dashboard', url_base=[]):

    filters_raw = {
        k: v for k, v in request.values.lists()
        if v != ['']
    }
    
    pages = {
        "dashboard": {
            "name": "Dashboard",
            "template": 'data.html.j2',
            "url": url_for(url_base[0], **{**url_base[1], **filters_raw}),
            "api_url": url_for(url_base[0], **{**url_base[1], **filters_raw, "filetype": "json"}),
        },
        "show-charities": {
            "name": "Show NGOs",
            "template": 'data-show-charities.html.j2',
            "url": url_for(url_base[0], **{**url_base[1], **filters_raw, "subpage": "show-charities"}),
            "api_url": url_for(url_base[0], **{**url_base[1], **filters_raw, "subpage": "show-charities", "filetype": "json"}),
        },
        "download": {
            "name": "Download",
            "template": 'data-download.html.j2',
            "url": url_for(url_base[0], **{**url_base[1], **filters_raw, "subpage": "download"}),
            "api_url": url_for(url_base[0], **{**url_base[1], **filters_raw, "subpage": "download", "filetype": "json"}),
        },
    }
    qgl_query = "charity_aggregation" if page=="dashboard" else "charity_list"

    filters = parse_filters(request.values)

    if "download_type" in request.values:
        return download_file(
            area=area,
            filters=filters,
            fields=request.values.getlist("fields"),
            filetype=request.values.get("download_type").lower(),
        )

    charity_data = fetch_charitybase(area["countries"], filters=filters, limit=30, skip=filters.get("skip", 0), query=qgl_query)
    charts = get_charts(charity_data, area["countries"]) if page=="dashboard" else {}

    if filetype=="json":

        inserts = {
            "selected-filters": render_template('_data_selected_filters.html.j2', filters=request.values, classification=CLASSIFICATION, area=area),
            "example-charities": render_template('_data_example_charities.html.j2', data=charity_data),
            "charity-count": "{:,.0f} UK NGO{}".format(charity_data["count"], "" if charity_data["count"] == 1 else "s"),
            "word-cloud": render_template('_data_word_cloud.html.j2', charts=charts),
            "max-countries-header": "{:,.0f}".format(filters.get("max_countries")),
        }

        if page=="show-charities":
            inserts["data-list"] = render_template(
                '_data_list_table.html.j2', pages=pages, active_page='show-charities', filters=request.values, data=charity_data)

        return jsonify(dict(
            area=area,
            data=charity_data,
            inserts=inserts,
            charts=charts,
            filters=request.values,
            pages=pages,
        ))

    iati_data = fetch_iati(area["countries"])

    return render_template(pages[page]["template"],
                           area=area,
                           data=charity_data,
                           iati_data=iati_data,
                           charts=charts,
                           filters=request.values,
                           pages=pages,
                           api_url=pages[page]['api_url'],
                           download_options=DOWNLOAD_OPTIONS,
                           classification=CLASSIFICATION,
                           similar_initiative=SIMILAR_INITIATIVE)


@bp.route('/charity/<charityid>')
def charity(charityid):
    charity_data = fetch_charitybase_fromids([charityid])
    data = charity_data["list"][0]
    if (data.get("website") or "").strip() != "":
        if not data["website"].startswith("http"):
            data["website"] = "//" + data["website"]
    countries = [c["id"] for c in data["areas"] if c["id"].startswith("D-")]
    data["countries"] = [c for c in COUNTRIES if c["id"] in countries]
    return render_template('charity.html.j2', data=data)

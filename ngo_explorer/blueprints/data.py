from flask import Blueprint, render_template, request, jsonify, url_for, Response

from ..utils.countries import get_country_groups, get_multiple_countries, COUNTRIES, SIMILAR_INITIATIVE
from ..utils.fetchdata import fetch_charitybase, fetch_iati, dict_to_gql
from ..utils.filters import CLASSIFICATION, parse_filters
from ..utils.download import DOWNLOAD_OPTIONS, download_file
from ..utils.charts import get_charts
from ..utils.utils import nested_to_record

bp = Blueprint('data', __name__, url_prefix='/')


@bp.route('/region/<regiontype>/<regionid>/<subpage>.<filetype>', methods=['GET', 'POST'])
@bp.route('/region/<regiontype>/<regionid>.<filetype>', methods=['GET', 'POST'])
@bp.route('/region/<regiontype>/<regionid>/<subpage>')
@bp.route('/region/<regiontype>/<regionid>')
def region(regionid, regiontype="continent", filetype="html", subpage="dashboard"):
    area = get_country_groups(as_dict=True).get((regiontype, regionid))

    if not area:
        return render_template(
            '404.html.j2',
            lookingfor='{} "{}" could not be found'.format(regiontype, regionid),
            countries=get_country_groups(),
            classification=CLASSIFICATION
        ), 404

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

    if not area:
        return render_template(
            '404.html.j2',
            lookingfor='Country "{}" could not be found'.format(
                countryid),
            countries=get_country_groups(),
            classification=CLASSIFICATION
        ), 404

    return data_page(
        area,
        filetype,
        subpage,
        url_base=[".country", {"countryid": countryid}]
    )

def data_page(area, filetype="html", page='dashboard', url_base=[]):

    filters_raw = {
        **{
            k: v if k in ["filter-countries", "filter-classification"] else v[0]
            for k, v in request.args.lists()
            if v != ['']
        },
        **{
            k: v if k in ["filter-countries", "filter-classification"] else v[0]
            for k, v in request.form.lists()
            if v != ['']
        }
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

    charity_data = fetch_charitybase(countries=area["countries"], filters=filters, limit=30, skip=filters.get("skip", 0), query=qgl_query)
    charts = get_charts(charity_data, area["countries"]) if page=="dashboard" else {}

    for c in area["countries"]:
        # whether the country has been filtered to the 
        c["filtered"] = c["id"] in filters.get("countries", []) if filters.get("countries") else True
        # number of charities in the selection that work in the country
        if "aggregate" in charity_data:
            c["charity_count"] = sum(
                [i["count"] for i in charity_data["aggregate"]["areas"]["buckets"] if i["key"] == c["id"]])

    if filetype=="json":

        inserts = {
            "selected-filters": render_template('_data_selected_filters.html.j2', filters=request.values, classification=CLASSIFICATION, area=area),
            "example-charities": render_template('_data_example_charities.html.j2', data=charity_data, area=area),
            "charity-count": "{:,.0f} UK NGO{}".format(charity_data["count"], "" if charity_data["count"] == 1 else "s"),
            "word-cloud": render_template('_data_word_cloud.html.j2', charts=charts),
            "max-countries-header": "{:,.0f}".format(filters.get("max_countries")),
        }

        if page=="show-charities":
            inserts["data-list"] = render_template(
                '_data_list_table.html.j2', pages=pages, active_page='show-charities', filters=request.values, data=charity_data, area=area)

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
    charity_data = fetch_charitybase(ids=[charityid])

    if charity_data["count"] == 0:
        return render_template(
            '404.html.j2',
            lookingfor='Charity "{}" could not be found'.format(
                charityid),
            countries=get_country_groups(),
            classification=CLASSIFICATION
        ), 404


    data = charity_data["list"][0]
    if (data.get("website") or "").strip() != "":
        if not data["website"].startswith("http"):
            data["website"] = "//" + data["website"]
    countries = [c["id"] for c in data["areas"] if c["id"].startswith("D-")]
    data["countries"] = [c for c in COUNTRIES if c["id"] in countries]
    return render_template('charity.html.j2', data=data)

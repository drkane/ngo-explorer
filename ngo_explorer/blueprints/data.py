from flask import Blueprint, render_template, request, jsonify, url_for, Response
from flask_babel import _

from ..utils.countries import get_country_groups, get_multiple_countries
from ..utils.fetchdata import fetch_charitybase, fetch_iati, fetch_iati_by_charity
from ..utils.filters import parse_filters
from ..utils.download import download_file
from ..utils.utils import nested_to_record

bp = Blueprint('data', __name__, url_prefix='/')


@bp.route('/region/<regiontype>/<regionid>/<subpage>.<filetype>', methods=['GET', 'POST'])
@bp.route('/region/<regiontype>/<regionid>.<filetype>', methods=['GET', 'POST'])
@bp.route('/region/<regiontype>/<regionid>/<subpage>')
@bp.route('/region/<regiontype>/<regionid>')
def region(regionid, regiontype="continent", filetype="html", subpage="dashboard"):

    if subpage not in ['dashboard', 'show-charities', 'download']:
        return render_template('404.html.j2'), 404

    area = get_country_groups(as_dict=True).get((regiontype, regionid))

    if not area:
        return render_template(
            '404.html.j2',
            lookingfor=_('%(regiontype)s "%(regionid)s" could not be found',
                         regiontype=regiontype, regionid=regionid),
        ), 404

    return data_page(
        area,
        filetype=filetype,
        page=subpage,
        url_base=[".region", {"regiontype": regiontype, "regionid": regionid}]
    )


@bp.route('/country/<countryid>/<subpage>.<filetype>', methods=['GET', 'POST'])
@bp.route('/country/<countryid>.<filetype>', methods=['GET', 'POST'])
@bp.route('/country/<countryid>/<subpage>')
@bp.route('/country/<countryid>')
def country(countryid, filetype="html", subpage='dashboard'):

    if subpage not in ['dashboard', 'show-charities', 'download']:
        return render_template('404.html.j2'), 404

    area = get_multiple_countries(countryid)

    if not area:
        return render_template(
            '404.html.j2',
            lookingfor=_('Country "%(countryid)s" could not be found',
                         countryid=countryid),
        ), 404

    return data_page(
        area,
        filetype=filetype,
        page=subpage,
        url_base=[".country", {"countryid": countryid}]
    )

def data_page(area=None, charity_ids=None, filetype="html", page='dashboard', url_base=[]):

    if request.method=="POST":
        filters_raw = request.form
    else:
        filters_raw = request.args
    filters_url = {
        k: v if k in ["filter-countries",
                        "filter-classification"] else v[0]
        for k, v in filters_raw.lists()
        if v != ['']
    }
    
    pages = {
        "dashboard": {
            "name": _("Dashboard"),
            "template": 'data.html.j2',
            "url": url_for(url_base[0], **{**url_base[1], **filters_url}),
            "api_url": url_for(url_base[0], **{**url_base[1], **filters_url, "filetype": "json"}),
        },
        "show-charities": {
            "name": _("Show NGOs"),
            "template": 'data-show-charities.html.j2',
            "url": url_for(url_base[0], **{**url_base[1], **filters_url, "subpage": "show-charities"}),
            "api_url": url_for(url_base[0], **{**url_base[1], **filters_url, "subpage": "show-charities", "filetype": "json"}),
        },
        "download": {
            "name": _("Download"),
            "template": 'data-download.html.j2',
            "url": url_for(url_base[0], **{**url_base[1], **filters_url, "subpage": "download"}),
            "api_url": url_for(url_base[0], **{**url_base[1], **filters_url, "subpage": "download", "filetype": "json"}),
        },
    }
    qgl_query = "charity_aggregation" if page=="dashboard" else "charity_list"

    filters = parse_filters(filters_raw)

    if "download_type" in request.values:
        return download_file(
            area=area,
            ids=charity_ids,
            filters=filters,
            fields=request.values.getlist("fields"),
            filetype=request.values.get("download_type").lower(),
        )

    all_charity_data = fetch_charitybase(query="all_charities")
    fetch_params = dict(
        filters=filters,
        limit=30,
        skip=filters.get("skip", 0),
        query=qgl_query,
        sort="random" if page=="dashboard" else "default"
    )
    if area and area.get("countries"):
        fetch_params['countries'] = area["countries"]
    if charity_ids:
        fetch_params['ids'] = charity_ids
    
    charity_data = fetch_charitybase(**fetch_params)
    charity_data.set_charts()

    iati_data = None
    if area and area.get("countries"):
        for c in area["countries"]:
            # whether the country has been filtered to the 
            c["filtered"] = c["id"] in filters.get("countries", []) if filters.get("countries") else True
            # number of charities in the selection that work in the country
            if getattr(charity_data, "aggregate", None):
                c["count"] = sum(
                    [i["count"] for i in charity_data.aggregate["areas"] if i["key"] == c["id"]])

        iati_data = fetch_iati(area["countries"])

    if filetype=="json":

        inserts = {
            "selected-filters": render_template('_data_selected_filters.html.j2', filters=filters_raw, area=area),
            "example-charities": render_template('_data_example_charities.html.j2', data=charity_data, area=area, all_charity_data=all_charity_data),
            "charity-count": "{:,.0f} UK NGO{}".format(charity_data.count, "" if charity_data.count == 1 else "s"),
            "word-cloud": render_template('_data_word_cloud.html.j2', data=charity_data),
            "max-countries-header": "{:,.0f}".format(filters.get("max_countries")),
        }

        if page=="show-charities":
            inserts["data-list"] = render_template(
                '_data_list_table.html.j2',
                pages=pages,
                active_page='show-charities',
                filters=filters_raw,
                data=charity_data,
                area=area
            )

        return jsonify(dict(
            area=area,
            inserts=inserts,
            charts=charity_data.get_charts(),
            filters=filters_raw,
            pages=pages,
        ))

    return render_template(pages[page]["template"],
                           area=area,
                           data=charity_data,
                           all_charity_data=all_charity_data,
                           iati_data=iati_data,
                           filters=filters_raw,
                           pages=pages,
                           region_type=url_base[1].get("regiontype"),
                           api_url=pages[page]['api_url'])


@bp.route('/charity/<charityid>')
def charity(charityid):
    charity_data = fetch_charitybase(ids=[charityid], all_finances=True)

    if charity_data.count == 0:
        return render_template(
            '404.html.j2',
            lookingfor=_('Charity "%(charityid)s" could not be found',
                         charityid=charityid),
        ), 404

    char = charity_data.get_charity()
    char.iati = fetch_iati_by_charity(getattr(char, "orgIds"))

    return render_template('charity.html.j2', data=char)

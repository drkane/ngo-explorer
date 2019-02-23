from flask import Blueprint, render_template, request, jsonify

from ..utils.countries import get_country_groups, get_multiple_countries
from ..utils.fetchdata import fetch_charitybase, fetch_iati
from ..utils.filters import CLASSIFICATION, parse_filters
from ..utils.download import DOWNLOAD_OPTIONS
from ..utils.charts import get_charts

bp = Blueprint('data', __name__, url_prefix='/')

SIMILAR_INITIATIVE = {
    "sen": [{
        "homepage": "https://pfongue.org/",
        "title": "Platform of European NGOs in Senegal",
        "directlink": "https://pfongue.org/-Cartographie-.html",
        "directlinktext": "Map of projects",
    }]
}


@bp.route('/region/<regiontype>/<regionid>', methods=['GET', 'POST'])
@bp.route('/region/<regiontype>/<regionid>/<subpage>')
@bp.route('/region/<regiontype>/<regionid>')
def region(regionid, regiontype="continent", filetype="html", subpage="dashboard"):
    area = get_country_groups(as_dict=True).get((regiontype, regionid))
    return data_page(area, filetype, subpage)


@bp.route('/country/<countryid>/<subpage>')
@bp.route('/country/<countryid>.<filetype>', methods=['GET', 'POST'])
@bp.route('/country/<countryid>')
def country(countryid, filetype="html", subpage='dashboard'):
    area = get_multiple_countries(countryid)
    return data_page(area, filetype, subpage)

def data_page(area, filetype="html", page='dashboard'):

    filters = parse_filters(request.values)
    charity_data = fetch_charitybase(area["countries"], filters=filters, limit=3)
    iati_data = fetch_iati(area["countries"])
    charts = get_charts(charity_data)
    base_path = request.path.replace(
        "/show-charities", "").replace("/download", "")

    if page=='show-charities':
        template = 'data-show-charities.html.j2'
    elif page == 'download':
        template = 'data-download.html.j2'
    else:
        template = 'data.html.j2'

    if filetype=="json":
        return jsonify(dict(
            area=area,
            data=charity_data,
            charts=charts,
            filters=filters,
        ))

    return render_template(template,
                           area=area,
                           data=charity_data,
                           iati_data=iati_data,
                           charts=charts,
                           filters=filters,
                           base_path=base_path,
                           download_options=DOWNLOAD_OPTIONS,
                           classification=CLASSIFICATION,
                           similar_initiative=SIMILAR_INITIATIVE)

import io
import csv

from flask import Blueprint, render_template, request, jsonify, url_for, Response
import xlsxwriter

from ..utils.countries import get_country_groups, get_multiple_countries
from ..utils.fetchdata import fetch_charitybase, fetch_iati
from ..utils.filters import CLASSIFICATION, parse_filters
from ..utils.download import DOWNLOAD_OPTIONS
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
            countries=area["countries"],
            filters=filters,
            fields=request.values.getlist("fields"),
            filetype=request.values.get("download_type").lower(),
        )

    charity_data = fetch_charitybase(area["countries"], filters=filters, limit=30, skip=filters.get("skip", 0), query=qgl_query)
    charts = get_charts(charity_data) if page=="dashboard" else {}

    if filetype=="json":

        inserts = {
            "selected-filters": render_template('_data_selected_filters.html.j2', filters=request.values, classification=CLASSIFICATION),
            "example-charities": render_template('_data_example_charities.html.j2', data=charity_data),
            "charity-count": "{:,.0f} UK NGO{}".format(charity_data["count"], "" if charity_data["count"] == 1 else "s")
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


def download_file(countries, filters, fields, filetype='csv'):
    raw_results = fetch_charitybase(
        countries,
        filters=filters,
        limit=30,
        skip=0,
        query="charity_list"
    )
    # raw_results = fetch_charities(filters, copy.copy(fields))

    if filetype.lower() in ["excel", "xlsx", "xls"]:
        filetype = 'xlsx'
    else:
        filetype = filetype.lower()

    fieldnames = set()
    results = []
    for r in raw_results["list"]:
        # if "countries" not in fields:
        #     del r["countries"]
        # if "areasOfOperation" not in fields:
        #     del r["areasOfOperation"]
        if filetype in ["xlsx", "csv"]:
            r = nested_to_record(r)
            # r = {k: r.get(k) for k in fields}
            for k, v in r.items():
                if isinstance(v, list):
                    if isinstance(v[0], dict):
                        v = [i.get("name", list(i.values())[0]) for i in v]
                    r[k] = ";".join(v)
            fieldnames.update(r.keys())
        results.append(r)

    fieldnames = ["id", "name"] + sorted([v for v in fieldnames if v not in ["id", "name"]])

    output = io.StringIO()
    if filetype == 'json':
        json.dump(results, output, indent=4)
        mimetype = 'application/json'
        extension = 'json'

    elif filetype == 'jsonl':
        for c in results:
            output.write(json.dumps(c, output))
        mimetype = 'application/x-jsonlines'
        extension = 'jsonl'

    elif filetype == 'xlsx':
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        worksheet.write_row(0, 0, fieldnames)
        row = 1
        for c in results:
            vals = [c.get(f) for f in fieldnames]
            worksheet.write_row(row, 0, vals)
            row += 1
        workbook.close()
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        extension = 'xlsx'

    else:  # assume csv if not given
        writer = csv.DictWriter(output, fieldnames=list(fieldnames))
        writer.writeheader()
        for c in results:
            writer.writerow(c)
        mimetype = 'text/csv'
        extension = 'csv'

    return Response(
        output.getvalue(),
        mimetype=mimetype,
        headers={
            "Content-disposition": "attachment; filename=download.{}".format(extension)
        }
    )

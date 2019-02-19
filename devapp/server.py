import os
import json
import csv
import io
import copy

import dash
import flask
import xlsxwriter

from .utils.utils import nested_to_record
from .data import fetch_charities

with open(os.path.join(os.path.dirname(__file__), 'templates', 'index.html')) as a:
    doc_template = a.read()

with open(os.path.join(os.path.dirname(__file__), 'utils', 'countries.json')) as a:
    COUNTRIES = json.load(a)['countries']

app = dash.Dash(
    __name__,
    external_stylesheets=[{
        "rel": "stylesheet",
        "href": "https://cdnjs.cloudflare.com/ajax/libs/tachyons/4.11.1/tachyons.css",
        "integrity": "sha256-A7VA5VRIGuWNdMLr/ydUEmYKKoBYqoRVF+Bwxup4KRg=",
        "crossorigin": "anonymous",
    }, {
        "rel": "stylesheet",
        "href": "https://fonts.googleapis.com/css?family=Abril+Fatface|Open+Sans",
    }],
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }],
    index_string=doc_template
)
app.scripts.config.serve_locally = True
server = app.server


@server.route('/download')
@server.route('/download.<filetype>')
def download_file(filetype='csv'):
    filters = json.loads(flask.request.args.get("filters"))
    fields = flask.request.args.get("fields", "").split(",")
    raw_results = fetch_charities(filters, copy.copy(fields))

    results = []
    for r in raw_results:
        if "countries" not in fields:
            del r["countries"]
        if "areasOfOperation" not in fields:
            del r["areasOfOperation"]
        if filetype in ["xlsx", "csv"]:
            r = nested_to_record(r)
            r = {k: r.get(k) for k in fields}
            for k, v in r.items():
                if isinstance(v, list):
                    r[k] = ";".join(v)
        results.append(r)

    output = io.StringIO()
    if filetype == 'json':
        json.dump(results, output, indent=4)
        mimetype = 'application/json'
        extension = 'json'

    elif filetype == 'jsonl':
        for c in results:
            json.dump(c, output)
        mimetype = 'application/x-jsonlines'
        extension = 'jsonl'

    elif filetype == 'xlsx':
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        worksheet.write_row(0, 0, fields)
        row = 1
        for c in results:
            worksheet.write_row(row, 0, list(c.values()))
            row += 1
        workbook.close()
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        extension = 'xlsx'

    else: # assume csv if not given
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for c in results:
            writer.writerow(c)
        mimetype = 'text/csv'
        extension = 'csv'

    return flask.Response(
        output.getvalue(),
        mimetype=mimetype,
        headers={
            "Content-disposition": "attachment; filename=download.{}".format(extension)
        }
    )

@server.route('/about')
def about_page():
    return flask.render_template('about.html')

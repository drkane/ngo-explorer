import os
import json
import csv
import io
import copy

import dash
import flask

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
    results = fetch_charities(filters, copy.copy(fields))

    for r in results:
        if "countries" not in fields:
            del r["countries"]
        if "areasOfOperation" not in fields:
            del r["areasOfOperation"]

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

    else: # assume csv if not given
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for c in results:
            r = nested_to_record(c)
            writer.writerow({k: r.get(k) for k in fields})
        mimetype = 'text/csv'
        extension = 'csv'

    return flask.Response(
        output.getvalue(),
        mimetype=mimetype,
        headers={
            "Content-disposition": "attachment; filename=download.{}".format(extension)
        }
    )

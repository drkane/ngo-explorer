import os
import json
import csv
import io

import dash
import flask

from .utils.utils import get_charity_row
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

server = app.server


@server.route('/download')
@server.route('/download.<filetype>')
def download_file(filetype='csv'):
    filters = json.loads(flask.request.args.get("filters"))
    results = fetch_charities(filters)

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
        writer = csv.DictWriter(output, fieldnames=[
            "Charity Number", "Name", "Income", "Countries of operation"])
        writer.writeheader()
        for c in results:
            writer.writerow(get_charity_row(c, number_format=False))
        mimetype = 'text/csv'
        extension = 'csv'

    return flask.Response(
        output.getvalue(),
        mimetype=mimetype,
        headers={
            "Content-disposition": "attachment; filename=download.{}".format(extension)
        }
    )

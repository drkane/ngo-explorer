import urllib.parse
import json

from dash.dependencies import Input, Output, State
import dash_html_components as html

from ..server import app
from ..data import fetch_charities

# fetch the results every time the filters change
@app.callback(
    Output(component_id='results-store', component_property='data'),
    [Input(component_id='filters-store', component_property='data')]
)
def update_results_json(filters):
    if filters:
        return fetch_charities(filters)
    return {}

# results being present or not
@app.callback(
    Output(component_id='results-wrapper', component_property='className'),
    [Input(component_id='results-store', component_property='data')],
    [State(component_id='results-wrapper', component_property='className')]
)
def show_hide_results_wrapper(results, existing_classes):
    classes = existing_classes.split(" ")
    classes = [c for c in existing_classes if c != 'dn']
    if not results:
        classes.append('dn')
    return " ".join(classes)

# new results trigger changes to the download link
@app.callback(
    Output(component_id='results-download-link', component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='filters-store', component_property='data'),
     Input(component_id='results-download-fields-main', component_property='values'),
     Input(component_id='results-download-fields-financial', component_property='values'),
     Input(component_id='results-download-fields-contact', component_property='values'),
     Input(component_id='results-download-fields-geo', component_property='values'),
     Input(component_id='results-download-fields-aoo', component_property='values'),
     ]
)
def update_results_link(_, filters, fields_main, fields_financial, fields_contact, fields_geo, fields_aoo):
    if not filters:
        return []
    filters = {k: v for k, v in filters.items() if v}

    fields = fields_main + fields_financial + fields_contact + fields_geo + fields_aoo
    query_args = urllib.parse.urlencode({
        "filters": json.dumps(filters),
        "fields": ",".join(fields),
    })
    return [
        html.A(className='pa2 w4 bg-light-yellow near-black link mr2',
               href="/download.xlsx?{}".format(query_args),
               children="Download for Excel"),
        html.A(className='pa2 w4 bg-light-yellow near-black link mr2',
               href="/download.csv?{}".format(query_args),
               children="Download as CSV"),
        html.A(className='pa2 w4 bg-light-yellow near-black link mr2',
               href="/download.json?{}".format(query_args),
               children="Download as JSON"),
    ]

# A change to the results triggers a change in the page heading
@app.callback(
    Output(component_id='results-count', component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_results_header(results, selected_rows):
    if not results:
        return ["No charities loaded", html.Div("Use filters to select charities", className="f5 gray")]
    if selected_rows:
        return "{:,.0f} charities found ({:,.0f} selected)".format(len(results), len(selected_rows))
    return "{:,.0f} charities found".format(len(results))

# Show the results container when we have results
@app.callback(
    Output(component_id='results-container', component_property='className'),
    [Input(component_id='results-store', component_property='data')],
)
def show_results_container(results):
    if not results:
        return "dn"
    return "db"

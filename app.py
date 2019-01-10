# -*- coding: utf-8 -*-
import os
import json
import urllib.parse
import io
import csv

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objs as go
import flask

from charitybase import CharityBase

def fetch_charities(regnos: list, aoo: list, max_countries: int=200):
    if not regnos and not aoo:
        return []

    charityBase = CharityBase(apiKey=os.getenv('CHARITYBASE_API_KEY'))

    query = {
        'fields': ['income.latest.total', 'income.annual', 'areasOfOperation'],
        'sort': 'income.latest.total:desc',
        'limit': 50,
        'skip': 0,
    }

    if regnos:
        query['ids.GB-CHC'] = ",".join(regnos)

    if aoo:
        query['areasOfOperation.id'] = ",".join(aoo)

    print(query)

    res = charityBase.charity.list(query)

    results = []
    for c in res.charities:
        c['countries'] = [
            ctry['name'] for ctry in c['areasOfOperation']
            if ctry['locationType'] == "Country" and ctry['name'] not in ['Scotland', 'Northern Ireland']
        ]
        if len(c['countries']) > max_countries:
            continue
        if not c['countries']:
            continue
        results.append(c)

    return results

with open('countries.json') as a:
    COUNTRIES = json.load(a)['countries']

app = dash.Dash(
    __name__,
    external_stylesheets=[{
        "rel": "stylesheet",
        "href": "https://cdnjs.cloudflare.com/ajax/libs/tachyons/4.11.1/tachyons.css",
        "integrity": "sha256-A7VA5VRIGuWNdMLr/ydUEmYKKoBYqoRVF+Bwxup4KRg=",
        "crossorigin": "anonymous",
    }],
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }],
)
app.title = 'Development Charities Data Explorer'

app.layout = html.Div(className="mw9 center ph3-ns sans-serif", children=[
    html.H1(children='Development Charities Data Explorer'),

    dcc.Markdown(children='''
An explorer for data on development charities based in the UK.
Uses data from the Charity Commission for England and Wales.
Powered by [CharityBase](https://charitybase.uk/).
    '''),

    html.Div(className='w-50', children=[
        html.H2("Select charities"),

        html.H3("Choose charities operating in a particular countries"),
        dcc.Dropdown(
            options=[
                {
                    'label': c['name'],
                    'value': c['id']
                } for c in COUNTRIES
            ],
            multi=True,
            id='area-of-operation-dropdown'
        ),
        html.Div([
            'Ignore any charities that work in more than',
            dcc.Input(
                placeholder='Enter a value...',
                type='number',
                value='180',
                id='max-countries',
                className='mh1 w3',
            ),
            'countries'
        ], className='mt2 f6'),

        html.H3("Filter by charity numbers"),
        html.P("Enter each charity number on a different line."),
        dcc.Textarea(
            id='charity-list',
            placeholder='Enter some charity numbers...',
            value='',
            style={'width': '100%'}
        ),

        html.Div(
            [html.Button(
                id='submit-button',
                n_clicks=0,
                children='Fetch data',
                className='link ph3 pv2 mb2 dib white bg-blue b--blue br3 ba'
            )],
            className='mt3',
        ),
    ]),

    html.Div(id='results-json', style={"display": "none"}),

    html.H2(id='results-count'),

    html.Div(
        className='cf',
        children=[
            html.Div(
                className='fl w-100 w-50-ns pr2',
                children=[
                    dt.DataTable(
                        id='results-list',
                        columns=[
                            {"name": 'Charity Number', "id": "Charity Number"},
                            {"name": 'Name', "id": "Name"},
                            {"name": 'Income', "id": "Income"},
                            {"name": 'Countries of operation',
                            "id": "Countries of operation"}
                        ],
                        data=[],
                        row_selectable='multi',
                        style_table={
                            'maxHeight': '500',
                            'maxWidth': '100%',
                        },
                        style_cell={
                            'minWidth': '0px', 'maxWidth': '180px',
                            'whiteSpace': 'normal'
                        },
                        n_fixed_columns=1,
                        n_fixed_rows=1,
                    ),
                    html.A("Download data", id="results-download-link")
                ]
            ),
            html.Div(
                className='fl w-100 w-50-ns pl2',
                children=[
                    html.H3("Financial history of charities"),
                    html.P(
                        "Figures given are in cash terms, without adjusting for inflation",
                        className="f6 gray i mb2 mt0"
                    ),
                    dcc.RadioItems(
                        options=[
                            {'label': 'Income', 'value': 'inc'},
                            {'label': 'Spending', 'value': 'exp'},
                        ],
                        value='inc',
                        id="financial-history-type",
                        labelClassName="pr2 f6",
                        inputClassName="mr1 f6",
                    ),
                    html.Div(id="finances-chart")
                ]
            ),
        ]
    ),
])


@app.callback(
    Output(component_id='results-json', component_property='children'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State(component_id='charity-list', component_property='value'),
     State(component_id='area-of-operation-dropdown', component_property='value'),
     State(component_id='max-countries', component_property='value')]
)
def update_results_json(_, input_value, aoo, max_countries):
    regnos = input_value.splitlines()
    max_countries = int(max_countries)
    results = fetch_charities(regnos, aoo, max_countries)

    return json.dumps(results)

@app.callback(
    Output(component_id='results-download-link', component_property='href'),
    [Input(component_id='results-json', component_property='children')],
    [State(component_id='charity-list', component_property='value'),
     State(component_id='area-of-operation-dropdown', component_property='value'),
     State(component_id='max-countries', component_property='value')]
)
def update_results_link(_, input_value, aoo, max_countries):
    regnos = input_value.splitlines()
    max_countries = int(max_countries)
    return "/download?{}".format(
        urllib.parse.urlencode({
            "regnos": json.dumps(regnos),
            "max_countries": max_countries,
            "aoo": json.dumps(aoo)
        })
    )


@app.callback(
    Output(component_id='results-count', component_property='children'),
    [Input(component_id='results-json', component_property='children')]
)
def update_results_header(results):
    results = json.loads(results)
    if not results:
        return "No charities loaded"
    return "{:,.0f} charities found".format(len(results))

@app.callback(
    Output(component_id='results-list', component_property='data'),
    [Input(component_id='results-json', component_property='children')],
)
def update_results_list(results, countries):
    results = json.loads(results)
    if not results:
        return []
    return [get_charity_row(c) for c in results]


def get_charity_row(c, number_format=True):
    if len(c['countries']) > 10:
        countries = "{:,.0f} countries".format(len(c['countries']))
    else:
        countries = ", ".join(c['countries'])

    income = c.get("income", {}).get(
        "latest", {}).get("total", None)
    if number_format:
        if income is None:
            income = 'Unknown'
        else:
            income = "£{:,.0f}".format(float(income))

    return {
        "Charity Number": c.get("ids", {}).get("GB-CHC", "Unknown"),
        # @TODO: currently DataTable doesn't support HTML in cells
        # "Name": html.A(
        #     href='https://charitybase.uk/charities/{}'.format(
        #         c.get("ids", {}).get("GB-CHC", "Unknown")),
        #     children=c.get("name", "Unknown"),
        #     target="_blank"
        # ),
        "Name": c.get("name", "Unknown"),
        "Income": income,
        "Countries of operation": countries
    }


@app.callback(
    Output(component_id='finances-chart', component_property='children'),
    [Input(component_id='results-json', component_property='children'),
     Input(component_id='results-list', component_property='derived_virtual_selected_rows'),
     Input(component_id="financial-history-type", component_property='value')]
)
def update_results_chart(results, selected_rows, field):
    results = json.loads(results)
    if not results:
        return

    if selected_rows:
        results = [v for k, v in enumerate(results) if k in selected_rows]

    field = {
        "inc": "income",
        "exp": "expend"
    }.get(field, "income")

    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=[f['financialYear']['end'] for f in c.get("income", {}).get("annual", [])],
                    y=[f[field] for f in c.get("income", {}).get("annual", [])],
                    name=c.get("name", "Unknown")
                ) for c in results
            ],
            layout=go.Layout(
                showlegend=False,
                margin=go.layout.Margin(l=40, r=0, t=40, b=30),
                yaxis=dict(
                    type='log',
                    autorange=True,
                    rangemode='tozero',
                    tickprefix='£',
                )
            )
        )
    )

server = app.server


@server.route('/download')
def download_file():
    filters = {
        "regnos": json.loads(flask.request.args.get("regnos")),
        "max_countries": int(flask.request.args.get("max_countries")),
        "aoo": json.loads(flask.request.args.get("aoo")),
    }
    results = fetch_charities(**filters)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["Charity Number", "Name", "Income", "Countries of operation"])
    writer.writeheader()
    for c in results:
        writer.writerow(get_charity_row(c, number_format=False))

    return flask.Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-disposition": "attachment; filename=download.csv"
        }
    )

if __name__ == '__main__':
    import requests_cache
    from dotenv import load_dotenv

    load_dotenv()
    requests_cache.install_cache()
    app.run_server(debug=True)

# -*- coding: utf-8 -*-
import os
import json

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objs as go

from charitybase import CharityBase

def fetch_charities(regnos: list, aoo: list):
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
    return res.charities

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
                ),
                className='fl w-100 w-50-ns pr2',
            ),
            html.Div(
                id='finances-chart',
                className='fl w-100 w-50-ns pl2'
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
    results = fetch_charities(regnos, aoo)

    new_results = []
    for c in results:
        c['countries'] = [
            ctry['name'] for ctry in c['areasOfOperation']
            if ctry['locationType'] == "Country" and ctry['name'] not in ['Scotland', 'Northern Ireland']
        ]
        if len(c['countries']) > max_countries:
            continue
        if not c['countries']:
            continue
        new_results.append(c)

    return json.dumps(new_results)

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
    [State(component_id='area-of-operation-dropdown', component_property='value')],
)
def update_results_list(results, countries):
    results = json.loads(results)
    if not results:
        return []

    rows = []
    for c in results:
        if len(c['countries']) > 10:
            countries = "{:,.0f} countries".format(len(c['countries']))
        else:
            countries = ", ".join(c['countries'])

        income = c.get("income", {}).get(
            "latest", {}).get("total", None)
        if income is None:
            income = 'Unknown'
        else:
            income = "£{:,.0f}".format(float(income))

        row = {
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
        rows.append(row)
    return rows


@app.callback(
    Output(component_id='finances-chart', component_property='children'),
    [Input(component_id='results-json', component_property='children'),
     Input(component_id='results-list', component_property='derived_virtual_selected_rows')]
)
def update_results_chart(results, selected_rows):
    results = json.loads(results)
    if not results:
        return

    if selected_rows:
        results = [v for k, v in enumerate(results) if k in selected_rows]

    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=[f['financialYear']['end'] for f in c.get("income", {}).get("annual", [])],
                    y=[f['income'] for f in c.get("income", {}).get("annual", [])],
                    name=c.get("name", "Unknown")
                ) for c in results
            ],
            layout=go.Layout(
                title='Financial history of charities',
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

if __name__ == '__main__':
    import requests_cache
    from dotenv import load_dotenv

    load_dotenv()
    requests_cache.install_cache()
    app.run_server(debug=True)

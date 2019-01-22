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

def fetch_charities(regnos: list, aoo: list, max_countries: int=200, include_oa: bool=True):
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

    if include_oa:
        query['causes.id'] = "106"

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

with open(os.path.join('utils', 'countries.json')) as a:
    COUNTRIES = json.load(a)['countries']

doc_template = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body class="bg-dark-gray near-white f6 open-sans">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
        </footer>
    </body>
</html>
'''

tabs_container_style = {
    'borderBottom': '2px solid #FBF1A9',
    'marginBottom': '16px',
}
tab_style = {
    'width': 'auto',
    'marginRight': '8px',
    'padding': '8px',
    'fontSize': '1.25rem',
    'color':  '#f4f4f4',
    'backgroundColor': 'inherit',
    'borderWidth': '1px 1px 0px 1px !important',
    'borderStyle': 'solid !important',
    'borderColor': 'gray !important',
}
tab_selected_style = {
    'width': 'auto',
    'margin-right': '8px',
    'padding': '8px',
    'fontSize': '1.25rem',
    'color':  '#f4f4f4',
    'backgroundColor': '#FBF1A9',
    'borderStyle': 'none !important',
}

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
app.title = 'Development Charities Data Explorer'

app.layout = html.Div(className="mw9 center ph3-ns mb4 cf", children=[

    html.Div(
        id='upload-csv-modal',
        className='dn',
        children=[
            html.Div(id='upload-csv-model-overlay',
                    className='w-100 h-100 absolute bg-dark-gray o-70'),
            html.Div(
                id='upload-csv-modal-content',
                className='w-100 h-100 absolute pa7',
                children=[
                    html.Div(className='bg-white dark-gray', children=[
                        html.Div(className='cf', children=[
                            html.Button(
                                id='close-upload-modal', className='fr pv1 ph2 ma1 near-white bg-light-yellow bn pointer f4 lh-none lh-solid', children='×'),
                        ]),
                        dcc.Tabs(
                            id="upload-tabs",
                            value='tab-1',
                            parent_className='',
                            content_className='pa3',
                            className='pt1 pl1 pr1',
                            style=tabs_container_style,
                            children=[
                                dcc.Tab(label='Paste a list of charities', value='tab-1', className='', style=tab_style, selected_style=tab_selected_style, children=[
                                    html.P("Enter each charity number on a different line."),
                                    dcc.Textarea(
                                        id='charity-list',
                                        placeholder='Enter some charity numbers...',
                                        value='',
                                        style={'width': '100%'}
                                    ),
                                ]),
                                dcc.Tab(label='Upload a CSV file', value='tab-2', className='', style=tab_style, selected_style=tab_selected_style, children=[
                                    html.P("Enter each charity number on a different line."),
                                ]),
                            ]
                        )
                    ]),
                ]
            ),
        ]
    ),

    html.H1(children=[
        'Development Charities Data Explorer',
        html.Span("alpha", className="gray f5 ml2 ttl")
    ], className='abril normal light-yellow pb3 bb b--gray ttu f2'),

    dcc.Markdown(children='''
An explorer for data on development charities based in the UK.
Uses data from the Charity Commission for England and Wales.
Powered by [CharityBase](https://charitybase.uk/).
    '''),

    html.Div(id='simple-filter', children=[
        html.P(className='mb4 f4 flex items-center', children=[
            "Show me charities operating in ",
            dcc.Dropdown(
                options=[],
                multi=True,
                id='area-of-operation-dropdown',
                className='inline-filter',
                placeholder='Country'
            ),
            html.Span(' or ', className='ph2'),
            html.Button(
                className='link underline bg-inherit bn light-yellow pa0 pointer',
                children='upload a list of charities',
                id='open-upload-modal',
            ),
            '.',
        ])
    ]),

    html.Div(className='fl w-25 pr2', children=[
        html.Div(className="pa2 bg-light-yellow white", children=[
            html.H2("Filters", className="pa0 ma0 normal ttu near-black"),
        ]),
        html.Div(className="pa2 ba bw1 b--light-yellow lh-copy", children=[
            html.Div(
                className='mb3',
                children=[

                ]
            ),
        ]),

        html.Div(className="pa2 bg-light-yellow white mt3", children=[
            html.H2("Advanced filters", className="pa0 ma0 normal ttu near-black"),
        ]),
        html.Div(className="pa2 ba bw1 b--light-yellow lh-copy", children=[
            html.Div(
                className='mb3',
                children=[
                    'Ignore any charities that work in more than',
                    html.Span(className='bb b--light-yellow pb1', children=[
                        dcc.Input(
                            placeholder='Enter a value...',
                            type='number',
                            value='180',
                            id='max-countries',
                            className='mh1 w3 bg-dark-gray bn near-white',
                        ),
                    ]),
                    'countries'
                ]
            ),

            html.Div(
                className='mb3',
                children=[
                    dcc.Checklist(
                        options=[
                            {'label': 'Only select from DAC-listed countries',
                             'value': 'dac'},
                        ],
                        values=['dac'],
                        id='include-dac',
                        inputClassName='mr2',
                    ),
                    html.A(
                        className='f6 i link gray underline',
                        href='http://www.oecd.org/dac/financing-sustainable-development/development-finance-standards/daclist.htm',
                        children='About DAC List countries (OECD)',
                        target='_blank',
                    )
                ]
            ),

            html.Div(
                className='mb3',
                children=[
                    dcc.Checklist(
                        options=[
                            {'label': 'Only include charities working in overseas aid and famine relief',
                             'value': 'cc-oa'},
                        ],
                        values=['cc-oa'],
                        id='include-cc-oa',
                        inputClassName='mr2',
                    )
                ]
            ),

            html.Div(
                className='mt3',
                children=[
                    html.Button(
                        id='submit-button',
                        n_clicks=0,
                        children='Fetch data',
                        className='link ph3 pv2 mb2 dib white bg-blue b--blue br3 ba'
                    )
                ],
            ),
        ]),
    ]),

    html.Div(
        className='fl w-75 pl2',
        children=[
            html.H2(id='results-count'),
            html.Div(
                className="dn w-100",
                id="results-container",
                children=[
                    dcc.Tabs(id="tabs", value='tab-1', className='', style=tabs_container_style, children=[

                        # Dashboard tab
                        dcc.Tab(label='Dashboard', value='tab-1', className='', style=tab_style, selected_style=tab_selected_style, children=[
                            html.Div(
                                className='w-100',
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
                                    html.Div(id="finances-chart",
                                             className="h6")
                                ]
                            ),
                            html.Div(
                                className='w-100',
                                children=[
                                    html.H3("Where these charities work"),
                                    html.Div(id="area-of-operation-map",
                                             className="h6")
                                ]
                            ),
                        ]),

                        # Data tab
                        dcc.Tab(label='See all charities', value='tab-2', style=tab_style, selected_style=tab_selected_style, children=[
                            dt.DataTable(
                                id='results-list',
                                columns=[
                                    {"name": 'Charity Number',
                                        "id": "Charity Number"},
                                    {"name": 'Name', "id": "Name"},
                                    {"name": 'Income', "id": "Income"},
                                    {"name": 'Countries of operation',
                                     "id": "Countries of operation"}
                                ],
                                data=[],
                                row_selectable='multi',
                                style_as_list_view=True,
                                style_table={
                                    # 'maxHeight': '500',
                                    'maxWidth': '100%',
                                },
                                style_cell={
                                    'minWidth': '0px',
                                    'maxWidth': '180px',
                                    'whiteSpace': 'normal',
                                },
                                # n_fixed_columns=1,
                                # n_fixed_rows=1,
                            ),
                            html.A("Download data", id="results-download-link")
                        ]),
                    ]),
                ]
            ),
        ]
    ),

    dcc.Store(id='filters-store', storage_type='session'),
    dcc.Store(id='current-filters-store', storage_type='session'),
    dcc.Store(id='results-store', storage_type='session'),
])


# add the list of countries to the filter dropdown
@app.callback(
    Output(component_id='area-of-operation-dropdown',
           component_property='options'),
    [Input(component_id='include-dac', component_property='values')]
)
def get_country_list(include_dac):
    countries = [c for c in COUNTRIES if c['iso'] != "GB"]
    if 'dac' in include_dac:
        countries = [c for c in countries if c['dac_status']]
    return [{
        'label': c['name'],
        'value': c['id']
    } for c in countries]

# open and close the data upload modal
@app.callback(
    Output(component_id='upload-csv-modal', component_property='className'),
    [Input(component_id='open-upload-modal', component_property='n_clicks'),
     Input(component_id='close-upload-modal', component_property='n_clicks')]
)
def show_upload_modal(open_clicks, close_clicks):
    if not open_clicks:
        return 'dn'
    if (open_clicks and not close_clicks) or (open_clicks > close_clicks):
        return ''
    return 'dn'

# Update the filter store based on changed filters
@app.callback(
    Output(component_id='filters-store', component_property='data'),
    [Input(component_id='charity-list', component_property='value'),
     Input(component_id='area-of-operation-dropdown',
           component_property='value'),
     Input(component_id='max-countries', component_property='value'),
     Input(component_id='include-cc-oa', component_property='values')]
)
def update_filter_store(input_value, aoo, max_countries, include_oa):
    return {
        "aoo": aoo,
        "regnos": input_value.splitlines(),
        "max_countries": int(max_countries),
        "include_oa": 'cc-oa' in include_oa,
    }

# Update the fetch button when the filter changes
@app.callback(
    Output(component_id='submit-button', component_property='children'),
    [Input(component_id='filters-store', component_property='data'),
     Input(component_id='current-filters-store', component_property='data')]
)
def update_fetch_button(new_filters, current_filters):
    if new_filters == current_filters:
        return '_'
    return 'Filters have changed: update results'

@app.callback(
    Output(component_id='results-store', component_property='data'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State(component_id='filters-store', component_property='data')]
)
def update_results_json(_, filters):
    if filters:
        return fetch_charities(**filters)

@app.callback(
    Output(component_id='results-download-link', component_property='href'),
    [Input(component_id='results-store', component_property='data')],
    [State(component_id='filters-store', component_property='data')]
)
def update_results_link(_, filters):
    return "/download?{}".format(
        urllib.parse.urlencode(filters)
    )

@app.callback(
    Output(component_id='current-filters-store', component_property='data'),
    [Input(component_id='results-store', component_property='data')],
    [State(component_id='filters-store', component_property='data')]
)
def update_results_link(_, filters):
    return filters


@app.callback(
    Output(component_id='results-count', component_property='children'),
    [Input(component_id='results-store', component_property='data')]
)
def update_results_header(results):
    if not results:
        return ["No charities loaded", html.Div("Use filters to select charities", className="f5 gray")]
    return "{:,.0f} charities found".format(len(results))

@app.callback(
    Output(component_id='results-list', component_property='data'),
    [Input(component_id='results-store', component_property='data')],
)
def update_results_list(results):
    if not results:
        return []
    return [get_charity_row(c) for c in results]

@app.callback(
    Output(component_id='results-container', component_property='className'),
    [Input(component_id='results-store', component_property='data')],
)
def show_results_container(results):
    if not results:
        return "dn"
    return "db"


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
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list', component_property='derived_virtual_selected_rows'),
     Input(component_id="financial-history-type", component_property='value')]
)
def update_results_chart(results, selected_rows, field):
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


@app.callback(
    Output(component_id='area-of-operation-map', component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list', component_property='derived_virtual_selected_rows')]
)
def update_results_map(results, selected_rows):
    if not results:
        return

    if selected_rows:
        results = [v for k, v in enumerate(results) if k in selected_rows]

    countries = {}
    for c in results:
        for ctry in c['areasOfOperation']:
            for ctry_iso in COUNTRIES:
                if ctry['id'] != ctry_iso['id']:
                    continue
                if ctry_iso['iso'] not in countries:
                    countries[ctry_iso['iso']] = 0
                countries[ctry_iso['iso']] += 1

    return dcc.Graph(
        figure=go.Figure(
            data=[dict(
                type='choropleth',
                locations=list(countries.keys()),
                z=list(countries.values()),
                text=list(countries.keys()),
                colorscale=[[0, "rgb(5, 10, 172)"], [0.35, "rgb(40, 60, 190)"], [0.5, "rgb(70, 100, 245)"],
                            [0.6, "rgb(90, 120, 245)"], [0.7, "rgb(106, 137, 247)"], [1, "rgb(220, 220, 220)"]],
                autocolorscale=False,
                reversescale=True,
                marker=dict(
                    line=dict(
                        color='rgb(180,180,180)',
                        width=0.5
                    )),
            )],
            layout=go.Layout(
                geo = dict(
                    showframe = False,
                    showcoastlines = False,
                    projection = dict(
                        type = 'natural earth'
                    )
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

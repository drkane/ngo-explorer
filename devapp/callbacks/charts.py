import datetime

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from ..server import app, COUNTRIES
from ..utils.utils import date_to_financial_year, get_scaling_factor

DEFAULT_LAYOUT = {
    'yaxis': {
        'automargin': True,
        'rangemode': 'tozero',
    },
    'xaxis': {
        'automargin': True,
    },
    # 'paper_bgcolor': '#444',
    # 'plot_bgcolor': '#444',
    # 'font': dict(
    #     color='#f4f4f4',
    # ),
    'margin': go.layout.Margin(
        l=40,
        r=0,
        b=40,
        t=0,
        pad=4
    ),
    'clickmode': 'event+select',
    'dragmode': 'select',
}


@app.callback(
    Output(component_id='aggregate-finances-chart',
           component_property='figure'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_aggregate_finances_chart(results, selected_rows):
    if not results:
        return {'data': [], 'layout': DEFAULT_LAYOUT}

    if selected_rows:
        results = [v for k, v in enumerate(results) if k in selected_rows]


    financial_years = {}

    for c in results:
        for f in c.get("income", {}).get("annual", []):
            fy = date_to_financial_year(f['financialYear']['end'][0:10])
            if fy not in financial_years:
                financial_years[fy] = {"Income": 0, "Spending": 0, "Count": 0}
            financial_years[fy]["Income"] += f["income"] if f["income"] else 0
            financial_years[fy]["Spending"] += f["expend"] if f["expend"] else 0
            financial_years[fy]["Count"] += 1 if (f["expend"] or f["income"]) else 0

    # if we're showing more than 5 results, then hide any years where we have less than half the data
    if len(results) > 5:
        financial_years = {k: v for k, v in financial_years.items() if (v["Count"] / len(results)) > 0.5}

    colours = {
        "Income": '#fbf1a9',
        "Spending": '#ccc',
    }

    scaling = get_scaling_factor(
        max([v["Income"] for fy, v in financial_years.items()] + [v["Spending"] for fy, v in financial_years.items()])
    )

    return go.Figure(
        data=[
            dict(
                x=list(financial_years.keys()),
                y=[v[f] / scaling[0] for fy, v in financial_years.items()],
                name=f,
                type='scatter',
            ) for f in ["Income", "Spending"]
        ],
        layout=DEFAULT_LAYOUT,
    )


@app.callback(
    Output(component_id='classification-causes-chart',
           component_property='figure'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_classification_causes_chart(results, selected_rows):
    return update_classification_chart(results, selected_rows, "causes")


@app.callback(
    Output(component_id='causes-filter', component_property='value'),
    [Input(component_id='classification-causes-chart',
           component_property='selectedData')],
    [State(component_id='causes-filter', component_property='options'),
     State(component_id='causes-filter', component_property='value')]
)
def selected_classification_causes_chart(selectedPoints, filter_options, existing_values):
    return update_selected_points(selectedPoints, filter_options, existing_values)

@app.callback(
    Output(component_id='classification-beneficiaries-chart',
           component_property='figure'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_classification_beneficiaries_chart(results, selected_rows):
    return update_classification_chart(results, selected_rows, "beneficiaries")


@app.callback(
    Output(component_id='beneficiary-filter', component_property='value'),
    [Input(component_id='classification-beneficiaries-chart',
           component_property='selectedData')],
    [State(component_id='beneficiary-filter', component_property='options'),
     State(component_id='beneficiary-filter', component_property='value')]
)
def selected_classification_beneficiary_chart(selectedPoints, filter_options, existing_values):
    return update_selected_points(selectedPoints, filter_options, existing_values)

@app.callback(
    Output(component_id='classification-operations-chart',
           component_property='figure'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_classification_operations_chart(results, selected_rows):
    return update_classification_chart(results, selected_rows, "operations")


@app.callback(
    Output(component_id='operation-filter', component_property='value'),
    [Input(component_id='classification-operations-chart', component_property='selectedData')],
    [State(component_id='operation-filter', component_property='options'),
     State(component_id='operation-filter', component_property='value')]
)
def selected_classification_operations_chart(selectedPoints, filter_options, existing_values):
    return update_selected_points(selectedPoints, filter_options, existing_values)


def update_selected_points(selectedPoints, filter_options, existing_values):
    if selectedPoints:
        selectedPoints = [i['y'] for i in selectedPoints.get('points', [])]
        existing_values = [
            i['value'] for i in filter_options if i['label'] in selectedPoints
        ]
    return existing_values


def update_classification_chart(results, selected_rows, class_type):
    if not results:
        return {'data': [], 'layout': DEFAULT_LAYOUT}

    if selected_rows:
        results = [v for k, v in enumerate(results) if k in selected_rows]

    categories = {}
    for c in results:
        for f in c.get(class_type, [{}]):
            if f["name"] not in categories:
                categories[f["name"]] = 0
            categories[f["name"]] += 1

    categories = dict(sorted(categories.items(), key=lambda x: -x[1]))

    return go.Figure(
        data=[
            dict(
                y=list(categories.keys()),
                x=list(categories.values()),
                name="Charities",
                type='bar',
                orientation='h',
            )
        ],
        layout=DEFAULT_LAYOUT,
    )

@app.callback(
    Output(component_id='summary-numbers',
           component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_summary_numbers(results, selected_rows):
    if not results:
        return []

    if selected_rows:
        results = [v for k, v in enumerate(results) if k in selected_rows]

    total_income = 0
    countries = {}
    for c in results:
        latest_income = c.get("income", {}).get("latest", {}).get("total")
        total_income += latest_income
        for ctry in c['areasOfOperation']:
            for ctry_iso in COUNTRIES:
                if ctry['id'] != ctry_iso['id']:
                    continue
                if ctry_iso['iso'] not in countries:
                    countries[ctry_iso['iso']] = 0
                countries[ctry_iso['iso']] += 1

    scaling = get_scaling_factor(total_income)

    return [
        html.Div(
            className='fl f4 b pa4 mr3 bg-light-yellow near-black tc',
            children=[
                html.Span(
                    className='f3',
                    children="{:,.0f}".format(len(results)),
                ),
                html.Br(),
                "charities"
            ],
        ),
        html.Div(
            className='fl f4 b pa4 mr3 bg-light-yellow near-black tc',
            children=[
                html.Span(
                    className='f3',
                    children="£{}".format(scaling[2].format(total_income / scaling[0])),
                ),
                html.Br(),
                "income",
            ],
        ),
        html.Div(
            className='fl f4 b pa4 mr3 bg-light-yellow near-black tc',
            children=[
                "Operating in",
                html.Br(),
                html.Span(
                    className='f3',
                    children="{:,.0f}".format(len(countries)),
                ),
                html.Br(),
                "countries",
            ],
        ),
    ]


@app.callback(
    Output(component_id='income-band-chart',
           component_property='figure'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_income_band_chart(results, selected_rows):
    if not results:
        return {'data': [], 'layout': DEFAULT_LAYOUT}

    if selected_rows:
        results = [v for k, v in enumerate(results) if k in selected_rows]

    income_bands = [
        ("Over £100m", 100000000),
        ("£40m-£100m",  40000000),
        ("£10m-£40m",   10000000),
        ("£3m-£10m",     3000000),
        ("£1m-£3m",      1000000),
        ("£500k-£1m",     500000),
        ("£100k-£500k",   100000),
        ("£10k-£100k",     10000),
        ("Under £10k",         0),
    ]

    income_band_results = {v[0]: {"count": 0, "income": 0}
                           for v in income_bands[::-1]}
    for c in results:
        latest_income = c.get("income", {}).get("latest", {}).get("total")
        for i in income_bands:
            if latest_income > i[1]:
                income_band_results[i[0]]["count"] += 1
                income_band_results[i[0]]["income"] += latest_income
                break

    return go.Figure(
        data=[
            dict(
                x=list(income_band_results.keys()),
                y=[i["count"] for i in income_band_results.values()],
                name="Charities",
                type='bar',
            ),
            dict(
                x=list(income_band_results.keys()),
                y=[i["income"] for i in income_band_results.values()],
                name="Income",
                type='bar',
            )
        ],
        layout=DEFAULT_LAYOUT,
    )

@app.callback(
    Output(component_id='registered-region-chart',
           component_property='figure'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_registered_region_chart(results, selected_rows):
    if not results:
        return {'data': [], 'layout': DEFAULT_LAYOUT}

    if selected_rows:
        results = [v for k, v in enumerate(results) if k in selected_rows]

    regions = {}
    for c in results:
        region = c.get("contact", {}).get("geo", {}).get("region")
        if not region:
            region = "Unknown"
        latest_income = c.get("income", {}).get("latest", {}).get("total")
        if region not in regions:
            regions[region] = {"count": 0, "income": 0}
        regions[region]["count"] += 1
        regions[region]["income"] += latest_income

    regions = dict(sorted(regions.items(), key=lambda x: -x[1]["count"] if x[0] != "Unknown" else float("inf")))

    return go.Figure(
        data=[
            dict(
                y=list(regions.keys()),
                x=[i["count"] for i in regions.values()],
                name="Charities",
                type='bar',
                orientation='h',
            ),
        ],
        layout=DEFAULT_LAYOUT,
    )


@app.callback(
    Output(component_id='area-of-operation-map',
           component_property='figure'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list', component_property='derived_virtual_selected_rows')]
)
def update_results_map(results, selected_rows):
    if not results:
        return {'data': [], 'layout': DEFAULT_LAYOUT}

    if selected_rows:
        results = [v for k, v in enumerate(results) if k in selected_rows]

    countries = {}
    for c in results:
        for ctry in c['areasOfOperation']:
            for ctry_iso in COUNTRIES:
                if ctry['id'] != ctry_iso['id'] or ctry_iso['iso'] == 'GBR':
                    continue
                if ctry_iso['iso'] not in countries:
                    countries[ctry_iso['iso']] = {"count": 0, "name": ctry_iso['name']}
                countries[ctry_iso['iso']]["count"] += 1

    return go.Figure(
        data=[
            dict(
                type='choropleth',
                locations=list(countries.keys()),
                z=[c["count"] for c in countries.values()],
                text=[c["name"] for c in countries.values()],
                colorscale=[[0, "rgb(5, 10, 172)"], [0.35, "rgb(40, 60, 190)"], [0.5, "rgb(70, 100, 245)"],
                            [0.6, "rgb(90, 120, 245)"], [0.7, "rgb(106, 137, 247)"], [1, "rgb(220, 220, 220)"]],
                autocolorscale=False,
                reversescale=True,
                marker=dict(
                    line=dict(
                        color='#eee',
                        width=0.5
                    )
                ),
                hoverinfo='text+z',
            ),
            dict(
                type='choropleth',
                locations=['GBR'],
                z=[1],
                text=['GBR'],
                colorscale=[[0, "#fbf1a9"], [1, "#fbf1a9"]],
                autocolorscale=False,
                reversescale=True,
                showscale=False,
                marker=dict(
                    line=dict(
                        color='#fbf1a9',
                        width=1
                    )
                ),
                hoverinfo='skip',
            )
        ],
        layout=go.Layout(
            geo=dict(
                showframe=False,
                showcoastlines=False,
                showland=True,
                landcolor='#eee',
                projection=dict(
                    type='natural earth'
                ),
                # bgcolor='#444',
            ),
            # paper_bgcolor='#444',
            # plot_bgcolor='#444',
            font=dict(
                # color='#f4f4f4',
            ),
            margin=dict(l=0, r=0, t=0, b=0),
        )
    )

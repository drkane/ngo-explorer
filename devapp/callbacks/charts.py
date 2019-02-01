import datetime

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash_chartjs import ChartJS

from ..server import app, COUNTRIES
from ..utils.utils import date_to_financial_year, get_scaling_factor

@app.callback(
    Output(component_id='finances-chart', component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows'),
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

    return ChartJS(
        type='line',
        data=dict(
            datasets=[
                {
                    'label': c.get("name", "Unknown"),
                    'data': [{
                        'x': datetime.datetime.strptime(f['financialYear']['end'][0:10], "%Y-%m-%d"),
                        'y': f[field]
                    } for f in c.get("income", {}).get("annual", [])],
                    'fill': False,
                    'borderColor': 'gray',
                    'lineTension': 0,
                    'pointRadius': 0,
                } for c in results
            ],
        ),
        options=dict(
            legend=dict(
                labels=dict(
                    fontColor='#ccc',
                ),
                display=False,
            ),
            scales=dict(
                xAxes=[dict(
                    type='time',
                    ticks=dict(
                        min=1,
                    ),
                )],
                yAxes=[dict(
                    type='logarithmic',
                )],
            ),
        ),
    )

@app.callback(
    Output(component_id='aggregate-finances-chart',
           component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_aggregate_finances_chart(results, selected_rows):
    if not results:
        return

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

    return ChartJS(
        type='line',
        data=dict(
            labels=list(financial_years.keys()),
            datasets=[
                {
                    'label': f,
                    'data': [v[f] / scaling[0] for fy, v in financial_years.items()],
                    'fill': False,
                    'borderColor': colours.get(f),
                    'lineTension': 0,
                    'pointRadius': 1,
                } for f in ["Income", "Spending"]
            ],
        ),
        options=dict(
            legend=dict(
                labels=dict(
                    fontColor='#ccc',
                ),
                display=True,
            ),
            scales=dict(
                xAxes=[dict(
                    gridLines=dict(
                        display=False
                    ),
                    ticks=dict(
                        fontColor='#ccc',
                    ),
                )],
                yAxes=[dict(
                    type='linear',
                    gridLines=dict(
                        display=False
                    ),
                    ticks=dict(
                        beginAtZero=True,
                        min=0,
                        fontColor='#ccc',
                    ),
                )],
            ),
        ),
    )


@app.callback(
    Output(component_id='classification-causes-chart',
           component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_classification_causes_chart(results, selected_rows):
    return update_classification_chart(results, selected_rows, "causes")


@app.callback(
    Output(component_id='classification-beneficiaries-chart',
           component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_classification_beneficiaries_chart(results, selected_rows):
    return update_classification_chart(results, selected_rows, "beneficiaries")


@app.callback(
    Output(component_id='classification-operations-chart',
           component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_classification_operations_chart(results, selected_rows):
    return update_classification_chart(results, selected_rows, "operations")


def update_classification_chart(results, selected_rows, class_type):
    if not results:
        return

    if selected_rows:
        results = [v for k, v in enumerate(results) if k in selected_rows]

    categories = {}
    for c in results:
        for f in c.get(class_type, [{}]):
            if f["name"] not in categories:
                categories[f["name"]] = 0
            categories[f["name"]] += 1

    categories = dict(sorted(categories.items(), key=lambda x: -x[1]))

    return ChartJS(
        type='horizontalBar',
        data=dict(
            labels=list(categories.keys()),
            datasets=[
                {
                    'label': "Charities",
                    'data': list(categories.values()),
                    'backgroundColor': '#fbf1a9',
                }
            ],
        ),
        options=dict(
            legend=dict(
                labels=dict(
                    fontColor='#ccc',
                ),
                display=False,
            ),
            scales=dict(
                yAxes=[dict(
                    ticks=dict(
                        fontColor='#ccc',
                    ),
                )],
                xAxes=[dict(
                    ticks=dict(
                        beginAtZero=True,
                        min=0,
                        fontColor='#ccc',
                    ),
                )],
            ),
        ),
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
        return

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
           component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_income_band_chart(results, selected_rows):
    if not results:
        return

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

    return ChartJS(
        type='bar',
        data=dict(
            labels=list(income_band_results.keys()),
            datasets=[
                {
                    'label': "Charities",
                    'data': [i["count"] for i in income_band_results.values()],
                    'backgroundColor': '#fbf1a9',
                    'yAxisID': 'y-axis-1',
                }, {
                    'label': "Latest income",
                    'data': [i["income"] for i in income_band_results.values()],
                    'backgroundColor': '#fff',
                    'yAxisID': 'y-axis-2',
                }
            ],
        ),
        options=dict(
            legend=dict(
                labels=dict(
                    fontColor='#ccc',
                ),
                display=False,
            ),
            scales=dict(
                xAxes=[dict(
                    ticks=dict(
                        fontColor='#ccc',
                    ),
                )],
                yAxes=[
                    dict(
                        ticks=dict(
                            beginAtZero=True,
                            min=0,
                            fontColor='#ccc',
                        ),
                        position='left',
                        id='y-axis-1',
                    ),
                    dict(
                        ticks=dict(
                            beginAtZero=True,
                            min=0,
                            fontColor='#ccc',
                        ),
                        position='right',
                        id='y-axis-2',
                    )
                ],
            ),
        ),
    )

@app.callback(
    Output(component_id='registered-region-chart',
           component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_registered_region_chart(results, selected_rows):
    if not results:
        return

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

    return ChartJS(
        type='horizontalBar',
        data=dict(
            labels=list(regions.keys()),
            datasets=[
                {
                    'label': "Charities",
                    'data': [i["count"] for i in regions.values()],
                    'backgroundColor': '#fbf1a9',
                }
            ],
        ),
        options=dict(
            legend=dict(
                labels=dict(
                    fontColor='#ccc',
                ),
                display=False,
            ),
            scales=dict(
                yAxes=[dict(
                    ticks=dict(
                        fontColor='#ccc',
                    ),
                )],
                xAxes=[
                    dict(
                        ticks=dict(
                            beginAtZero=True,
                            min=0,
                            fontColor='#ccc',
                        )
                    )
                ],
            ),
        ),
    )


@app.callback(
    Output(component_id='area-of-operation-map',
           component_property='children'),
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
                if ctry['id'] != ctry_iso['id'] or ctry_iso['iso']=='GBR':
                    continue
                if ctry_iso['iso'] not in countries:
                    countries[ctry_iso['iso']] = {"count": 0, "name": ctry_iso['name']}
                countries[ctry_iso['iso']]["count"] += 1

    return dcc.Graph(
        figure=go.Figure(
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
                    landcolor='#555',
                    projection=dict(
                        type='natural earth'
                    ),
                    bgcolor='#444',
                ),
                paper_bgcolor='#444',
                plot_bgcolor='#444',
                font=dict(
                    color='#f4f4f4',
                ),
                margin=dict(l=0, r=0, t=0, b=0),
            )
        )
    )

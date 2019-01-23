from dash.dependencies import Input, Output
import dash_core_components as dcc
import plotly.graph_objs as go

from ..server import app, COUNTRIES

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

    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=[f['financialYear']['end']
                        for f in c.get("income", {}).get("annual", [])],
                    y=[f[field]
                        for f in c.get("income", {}).get("annual", [])],
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
                geo=dict(
                    showframe=False,
                    showcoastlines=False,
                    projection=dict(
                        type='natural earth'
                    )
                )
            )
        )
    )

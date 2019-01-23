import urllib.parse

from dash.dependencies import Input, Output, State
import dash_html_components as html

from ..server import app
from ..data import fetch_charities

# When filters change, update the filters store
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

# changing the filters store triggers a change in the submit button
# it compare the new filters against the cached ones to check whether
# the submit button should be updated
@app.callback(
    Output(component_id='submit-button', component_property='children'),
    [Input(component_id='filters-store', component_property='data'),
     Input(component_id='current-filters-store', component_property='data')]
)
def update_fetch_button(new_filters, current_filters):
    if new_filters == current_filters:
        return '_'
    return 'Filters have changed: update results'

# pressing the fetch data button triggers a data fetch
@app.callback(
    Output(component_id='results-store', component_property='data'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State(component_id='filters-store', component_property='data')]
)
def update_results_json(_, filters):
    if filters:
        return fetch_charities(**filters)

# new results trigger changes to the download link
@app.callback(
    Output(component_id='results-download-link', component_property='href'),
    [Input(component_id='results-store', component_property='data')],
    [State(component_id='filters-store', component_property='data')]
)
def update_results_link(_, filters):
    if not filters:
        return '#'
    filters = {k: v for k, v in filters.items() if v}
    return "/download?{}".format(
        urllib.parse.urlencode(filters)
    )

# on new results, the cached filters are updated to allow checking
# of when they are changed
@app.callback(
    Output(component_id='current-filters-store', component_property='data'),
    [Input(component_id='results-store', component_property='data')],
    [State(component_id='filters-store', component_property='data')]
)
def update_current_filters(_, filters):
    return filters

# A change to the results triggers a change in the page heading
@app.callback(
    Output(component_id='results-count', component_property='children'),
    [Input(component_id='results-store', component_property='data')]
)
def update_results_header(results):
    if not results:
        return ["No charities loaded", html.Div("Use filters to select charities", className="f5 gray")]
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
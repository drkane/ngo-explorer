import operator

from dash.dependencies import Input, Output

from ..server import app, COUNTRIES
from ..components.countryfilter import COUNTRY_GROUPS


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
        'label': "All countries",
        'value': "__all"
    }] + [{
        'label': "{} - {}".format(c[1], c[2]),
        'value': c[0]
    } for c in COUNTRY_GROUPS] + [{
        'label': c['name'],
        'value': c['id']
    } for c in countries]


# filter countries if a selection made
@app.callback(
    Output('area-of-operation-dropdown', 'value'),
    [
        Input("country-group-{}".format(g[0]), 'n_clicks_timestamp')
        for g in COUNTRY_GROUPS
    ],
)
def update_country_groups(*args):
    args = list(zip(COUNTRY_GROUPS, [a if a else 0 for a in args]))
    clicked_item = max(args, key=operator.itemgetter(1))

    if clicked_item[1] == 0:
        return ['__all']

    return clicked_item[0][0]

from dash.dependencies import Input, Output

from ..server import app, COUNTRIES

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

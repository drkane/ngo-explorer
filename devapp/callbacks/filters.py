import operator

from dash.dependencies import Input, Output

from ..server import app, COUNTRIES
from ..components.countryfilter import COUNTRY_GROUPS, UNDP_GROUPS, DAC_OPTIONS


def determine_countries(aoo):

    countries = []
    country_groups = {
        i[0]: {
            "type": i[1],
            "label": i[2],
        } for i in COUNTRY_GROUPS
    }

    if not isinstance(aoo, list):
        aoo = [aoo]

    for item in aoo:

        if item == '__all':
            return [c['id'] for c in COUNTRIES if c['iso'] != "GB"]

        elif item.startswith('dac-'):
            if item == 'dac-all':
                countries.extend([c['id']
                                  for c in COUNTRIES if c['dac_status']])
            else:
                countries.extend([c['id']
                                  for c in COUNTRIES if c['dac_status']] == country_groups.get(item)['label'])

        elif item.startswith('undp-'):
            iso_codes = UNDP_GROUPS.get(country_groups.get(item)['label'], [])
            countries.extend([c['id']
                              for c in COUNTRIES if c['iso'] in iso_codes])

        else:
            countries.append(item)

    return countries


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
# @app.callback(
#     Output('area-of-operation-dropdown', 'value'),
#     [
#         Input("country-group-{}".format(g[0]), 'n_clicks_timestamp')
#         for g in COUNTRY_GROUPS
#     ],
# )
# def update_country_groups(*args):
#     args = list(zip(COUNTRY_GROUPS, [a if a else 0 for a in args]))
#     clicked_item = max(args, key=operator.itemgetter(1))

#     if clicked_item[1] == 0:
#         return ['__all']

#     return clicked_item[0][0]

# When filters change, update the filters store


@app.callback(
    Output(component_id='filters-store', component_property='data'),
    [Input(component_id='charity-list', component_property='value'),
     Input(component_id='area-of-operation-dropdown',
           component_property='value'),
     Input(component_id='max-countries', component_property='value'),
     Input(component_id='include-cc-oa', component_property='values'),
     Input(component_id='search', component_property='value'),
     Input(component_id='min-income', component_property='value'),
     Input(component_id='max-income', component_property='value'),
     Input(component_id='causes-filter', component_property='value'),
     Input(component_id='beneficiary-filter', component_property='value'),
     Input(component_id='operation-filter', component_property='value')]
)
def update_filter_store(input_value, aoo, max_countries, include_oa, search, min_income, max_income, causes, beneficiaries, operations):
    # because of <https://community.plot.ly/t/adding-ability-to-delete-numbers-from-input-type-number/12802>
    max_income = None if max_income == 0 else max_income
    return {
        "aoo": determine_countries(aoo),
        "regnos": input_value.splitlines(),
        "max_countries": int(max_countries),
        "include_oa": 'cc-oa' in include_oa,
        "search": search,
        "min_income": min_income,
        "max_income": max_income,
        "causes": causes,
        "beneficiaries": beneficiaries,
        "operations": operations
    }

# when clear button is pressed clear the values
@app.callback(
    Output(component_id='search', component_property='value'),
    [Input(component_id='clear-filters', component_property='n_clicks')]
)
def clear_search_box(clicked):
    return ""

import urllib.parse
import json

from dash.dependencies import Input, Output, State
import dash_html_components as html

from ..server import app, COUNTRIES
from ..data import fetch_charities
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
            countries.extend([c['id'] for c in COUNTRIES if c['iso'] in iso_codes])

        else:
            countries.append(item)

    return countries


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

# fetch the results every time the filters change
@app.callback(
    Output(component_id='results-store', component_property='data'),
    [Input(component_id='filters-store', component_property='data')]
)
def update_results_json(filters):
    if filters:
        return fetch_charities(filters)
    return {}

# results being present or not
@app.callback(
    Output(component_id='results-wrapper', component_property='className'),
    [Input(component_id='results-store', component_property='data')],
    [State(component_id='results-wrapper', component_property='className')]
)
def show_hide_results_wrapper(results, existing_classes):
    classes = existing_classes.split(" ")
    classes = [c for c in existing_classes if c != 'dn']
    if not results:
        classes.append('dn')
    return " ".join(classes)

# new results trigger changes to the download link
@app.callback(
    Output(component_id='results-download-link', component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='filters-store', component_property='data'),
     Input(component_id='results-download-fields-main', component_property='values'),
     Input(component_id='results-download-fields-financial', component_property='values'),
     Input(component_id='results-download-fields-contact', component_property='values'),
     Input(component_id='results-download-fields-geo', component_property='values'),
     Input(component_id='results-download-fields-aoo', component_property='values'),
     ]
)
def update_results_link(_, filters, fields_main, fields_financial, fields_contact, fields_geo, fields_aoo):
    if not filters:
        return []
    filters = {k: v for k, v in filters.items() if v}

    fields = fields_main + fields_financial + fields_contact + fields_geo + fields_aoo
    query_args = urllib.parse.urlencode({
        "filters": json.dumps(filters),
        "fields": ",".join(fields),
    })
    return [
        html.A(className='pa2 w4 bg-light-yellow near-black link mr2',
               href="/download.xlsx?{}".format(query_args),
               children="Download for Excel"),
        html.A(className='pa2 w4 bg-light-yellow near-black link mr2',
               href="/download.csv?{}".format(query_args),
               children="Download as CSV"),
        html.A(className='pa2 w4 bg-light-yellow near-black link mr2',
               href="/download.json?{}".format(query_args),
               children="Download as JSON"),
    ]

# A change to the results triggers a change in the page heading
@app.callback(
    Output(component_id='results-count', component_property='children'),
    [Input(component_id='results-store', component_property='data'),
     Input(component_id='results-list',
           component_property='derived_virtual_selected_rows')]
)
def update_results_header(results, selected_rows):
    if not results:
        return ["No charities loaded", html.Div("Use filters to select charities", className="f5 gray")]
    if selected_rows:
        return "{:,.0f} charities found ({:,.0f} selected)".format(len(results), len(selected_rows))
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

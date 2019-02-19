from dash.dependencies import Input, Output, State

from ..server import app
from ..utils.utils import get_charity_row

# Triggered by a change in the results
@app.callback(
    Output(component_id='results-list', component_property='data'),
    [Input(component_id='results-store', component_property='data')],
)
def update_results_list(results):
    if not results:
        return []
    return [get_charity_row(c) for c in results]

# Select all fields in the download
def results_download_select_all():
    def results_download_select_all_func(select_all, select_this_field, clear_all, clear_this_field, options, existing_values):
        select_all = select_all if select_all else 0
        select_this_field = select_this_field if select_this_field else 0
        clear_all = clear_all if clear_all else 0
        clear_this_field = clear_this_field if clear_this_field else 0

        if (select_all + select_this_field + clear_all + clear_this_field) == 0:
            return existing_values


        if max(select_all, select_this_field) > max(clear_all, clear_this_field):
            return [o['value'] for o in options]
        if max(select_all, select_this_field) < max(clear_all, clear_this_field):
            return []

        return existing_values
    return results_download_select_all_func


for i in ['main', 'financial', 'contact', 'aoo', 'geo']:
    app.callback(
        Output(component_id='results-download-fields-{}'.format(i), component_property='values'),
        [Input(component_id='results-download-select-all', component_property='n_clicks_timestamp'),
         Input(component_id='results-download-fields-{}-select-all'.format(i), component_property='n_clicks_timestamp'),
         Input(component_id='results-download-clear-all', component_property='n_clicks_timestamp'),
         Input(component_id='results-download-fields-{}-clear-all'.format(i), component_property='n_clicks_timestamp')],
        [State(component_id='results-download-fields-{}'.format(i), component_property='options'),
         State(component_id='results-download-fields-{}'.format(i), component_property='values')]
    )(
        results_download_select_all()
    )

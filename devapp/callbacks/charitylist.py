from dash.dependencies import Input, Output

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

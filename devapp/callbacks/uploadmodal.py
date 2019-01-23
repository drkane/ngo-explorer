from dash.dependencies import Input, Output

from ..server import app

# open and close the data upload modal
@app.callback(
    Output(component_id='upload-csv-modal', component_property='className'),
    [Input(component_id='open-upload-modal', component_property='n_clicks'),
     Input(component_id='close-upload-modal', component_property='n_clicks')]
)
def show_upload_modal(open_clicks, close_clicks):
    if not open_clicks:
        return 'dn'
    if (open_clicks and not close_clicks) or (open_clicks > close_clicks):
        return ''
    return 'dn'

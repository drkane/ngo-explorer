from dash.dependencies import Input, Output, State

from ..server import app

# open and close the data upload modal
@app.callback(
    Output(component_id='upload-csv-modal', component_property='className'),
    [Input(component_id='open-upload-modal', component_property='n_clicks_timestamp'),
     Input(component_id='close-upload-modal', component_property='n_clicks_timestamp')],
    [State(component_id='upload-csv-modal', component_property='className')]
)
def show_upload_modal(last_opened, last_closed, existing_styles):
    existing_styles = existing_styles.split(" ")
    last_opened = last_opened if last_opened else 0
    last_closed = last_closed if last_closed else 0
    if last_opened > last_closed:
        if 'dn' in existing_styles:
            existing_styles.remove('dn')
    else:
        if 'dn' not in existing_styles:
            existing_styles.append('dn')
    return " ".join(existing_styles)

# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html

from .server import app

from .components import *

app.title = 'NGO Explorer'
app.layout = html.Div(className="mw9 center ph3-ns mb4 cf", children=[
    # modals
    upload_modal(),

    # headers
    header(),
    countryfilter(),
    fetch_data_button(),

    # wrapper around results
    html.Div(children=[

        # sidebar
        html.Div(className='fl w-25 pr2', children=[
            basic_filters(),
            advanced_filters(),
        ]),

        # main window
        html.Div(
            id='results-wrapper',
            className='dn fl w-75 pl2',
            children=results()
        ),

    ]),

    # data stores
    dcc.Store(id='filters-store', storage_type='session'),
    dcc.Store(id='current-filters-store', storage_type='session'),
    dcc.Store(id='results-store', storage_type='session'),
])

from .callbacks import *

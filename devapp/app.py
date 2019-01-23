# -*- coding: utf-8 -*-
import os
import json

import dash_core_components as dcc
import dash_html_components as html

from .server import app

from .utils.utils import get_charity_row

from .components import *

app.title = 'Development Charities Data Explorer'
app.layout = html.Div(className="mw9 center ph3-ns mb4 cf", children=[
    # modals
    upload_modal(),

    # headers
    header(),
    countryfilter(),

    # sidebar
    html.Div(className='fl w-25 pr2', children=[
        basic_filters(),
        advanced_filters(),
        fetch_data_button(),
    ]),

    # main window
    html.Div(
        className='fl w-75 pl2',
        children=results()
    ),

    # data stores
    dcc.Store(id='filters-store', storage_type='session'),
    dcc.Store(id='current-filters-store', storage_type='session'),
    dcc.Store(id='results-store', storage_type='session'),
])

from .callbacks import *

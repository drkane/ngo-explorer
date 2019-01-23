import dash_core_components as dcc
import dash_html_components as html

from .tabs import TABS_CONTAINER_STYLE, TAB_STYLE, TAB_SELECTED_STYLE

def upload_modal():
    return html.Div(
        id='upload-csv-modal',
        className='dn',
        children=[
            html.Div(id='upload-csv-model-overlay',
                     className='w-100 h-100 absolute bg-dark-gray o-70'),
            html.Div(
                id='upload-csv-modal-content',
                className='w-100 h-100 absolute pa7',
                children=[
                    html.Div(className='bg-white dark-gray', children=[
                        html.Div(className='cf', children=[
                            html.Button(
                                id='close-upload-modal',
                                className='fr pv1 ph2 ma1 near-white bg-light-yellow bn pointer f4 lh-none lh-solid',
                                children='×'
                            ),
                        ]),
                        dcc.Tabs(
                            id="upload-tabs",
                            value='tab-1',
                            parent_className='',
                            content_className='pa3',
                            className='pt1 pl1 pr1',
                            style=TABS_CONTAINER_STYLE,
                            children=[
                                dcc.Tab(
                                    label='Paste a list of charities',
                                    value='tab-1',
                                    className='',
                                    style=TAB_STYLE,
                                    selected_style=TAB_SELECTED_STYLE,
                                    children=[
                                        html.P(
                                            "Enter each charity number on a different line."),
                                        dcc.Textarea(
                                            id='charity-list',
                                            placeholder='Enter some charity numbers...',
                                            value='',
                                            style={'width': '100%'}
                                        ),
                                    ]
                                ),
                                dcc.Tab(
                                    label='Upload a CSV file',
                                    value='tab-2',
                                    className='',
                                    style=TAB_STYLE,
                                    selected_style=TAB_SELECTED_STYLE,
                                    children=[
                                        html.P("Enter each charity number on a different line."),
                                    ]
                                ),
                            ]
                        )
                    ]),
                ]
            ),
        ]
    )

import dash_core_components as dcc
import dash_html_components as html

def countryfilter():
    return html.Div(id='simple-filter', children=[
        html.P(className='mb4 f4 flex items-center', children=[
            "Show charities operating in ",
            dcc.Dropdown(
                options=[],
                multi=True,
                id='area-of-operation-dropdown',
                className='inline-filter',
                placeholder='Country'
            ),
            html.Span(' or ', className='ph2'),
            html.Button(
                className='link underline bg-inherit bn light-yellow pa0 pointer',
                children='upload a list of charities',
                id='open-upload-modal',
            ),
            '.',
        ])
    ])

import dash_core_components as dcc
import dash_html_components as html

def sidebar_box(contents: list, title=None):
    return html.Div(className='mb3', children=[
        html.Div(className="pa2 bg-light-yellow white", children=[
            html.H2(title, className="pa0 ma0 normal ttu near-black"),
        ]) if title else None,
        html.Div(className="pa2 ba bw1 b--light-yellow lh-copy", children=[
            html.Div(
                className='mb3',
                children=contents
            ),
        ]),
    ])


def filter_item(contents: list, title=None):
    title = [html.H3(className='', children=title)] if title else []

    return html.Div(
        className='mb3',
        children=title + contents
    )


def basic_filters():
    return sidebar_box([
        search_filter(),
        income_range(),
    ], 'Filters')

def advanced_filters():
    return sidebar_box([
        max_countries_filter(),
        daclist_filter(),
        oa_filter()
    ], 'Advanced Filters')

def search_filter():
    return filter_item([
        dcc.Input(
            placeholder='Search name or activities',
            id='search',
            className='w-100 lh-copy',
        )
    ])

def income_range():
    return filter_item([
        dcc.Input(
            placeholder='Minimum',
            type='number',
            id='min-income',
            className='w-100 lh-copy',
        ),
        dcc.Input(
            placeholder='Maximum',
            type='number',
            id='max-income',
            className='w-100 lh-copy',
        ),
    ], "Narrow by size of charity")

def max_countries_filter():
    return filter_item([
        'Ignore any charities that work in more than',
        html.Span(className='bb b--light-yellow pb1', children=[
            dcc.Input(
                placeholder='Enter a value...',
                type='number',
                value='180',
                id='max-countries',
                className='mh1 w3 bg-dark-gray bn near-white',
            ),
        ]),
        'countries'
    ])

def daclist_filter():
    return filter_item([
        dcc.Checklist(
            options=[
                {'label': 'Only select from DAC-listed countries',
                 'value': 'dac'},
            ],
            values=['dac'],
            id='include-dac',
            inputClassName='mr2',
        ),
        html.A(
            className='f6 i link gray underline',
            href='http://www.oecd.org/dac/financing-sustainable-development/development-finance-standards/daclist.htm',
            children='About DAC List countries (OECD)',
            target='_blank',
        )
    ])

def oa_filter():
    return filter_item([
        dcc.Checklist(
            options=[
                {'label': 'Only include charities working in overseas aid and famine relief',
                    'value': 'cc-oa'},
            ],
            values=['cc-oa'],
            id='include-cc-oa',
            inputClassName='mr2',
        )
    ])

def fetch_data_button():
    return html.Div(
        className='mt3',
        children=[
            html.Button(
                id='submit-button',
                n_clicks=0,
                children='Fetch data',
                className='link ph3 pv2 mb2 dib white bg-blue b--blue br3 ba'
            )
        ],
    )

import dash_core_components as dcc
import dash_html_components as html

def sidebar_box(contents: list, title=None):
    return html.Div(className='mb3 bn bg-mid-gray', children=[
        html.Div(className="pa2 bg-light-yellow white", children=[
            html.H2(title, className="pa0 ma0 f5 bold ttu near-black"),
        ]) if title else None,
        html.Div(className="pa2 lh-copy", children=[
            html.Div(
                className='mb3',
                children=contents
            ),
        ]),
    ])


def filter_item(contents: list, title=None):
    title = [html.H3(className='f5 normal mv0', children=title)] if title else []

    return html.Div(
        className='mb3',
        children=title + contents
    )


def basic_filters():
    return sidebar_box([
        search_filter(),
        income_range(),
        causes_filter(),
        beneficiaries_filter(),
        operation_filter(),
    ], 'Filters')

def advanced_filters():
    return sidebar_box([
        max_countries_filter(),
        daclist_filter(),
        oa_filter()
    ], 'Base Filters')

def search_filter():
    return filter_item([
        dcc.Input(
            placeholder='Search name or activities',
            id='search',
            className='mw-100 lh-copy bb-light-yellow bg-inherit near-white pa2',
        )
    ])

def income_range():
    return filter_item([
        html.P(className='flex items-center', children=[
            'Between',
            dcc.Input(
                placeholder='Minimum',
                type='number',
                id='min-income',
                className='mh1 w-33 lh-copy bb-light-yellow bg-inherit near-white pa1',
            ),
            'and',
            dcc.Input(
                placeholder='Maximum',
                type='number',
                id='max-income',
                className='mh1 w-33 lh-copy bb-light-yellow bg-inherit near-white pa1',
            ),
        ])
    ], "Latest income")

def causes_filter():
    return filter_item([
        dcc.Dropdown(
            id='causes-filter',
            multi=True,
            options=[
                {"value": "101", "label": "General charitable purposes"},
                {"value": "102", "label": "Education/training"},
                {"value": "103", "label": "The advancement of health or saving of lives"},
                {"value": "104", "label": "Disability"},
                {"value": "105", "label": "The prevention or relief of poverty"},
                {"value": "106", "label": "Overseas aid/famine relief"},
                {"value": "107", "label": "Accommodation/housing"},
                {"value": "108", "label": "Religious activities"},
                {"value": "109", "label": "Arts/culture/heritage/science"},
                {"value": "110", "label": "Amateur sport"},
                {"value": "111", "label": "Animals"},
                {"value": "112", "label": "Environment/conservation/heritage"},
                {"value": "113", "label": "Economic/community development/employment"},
                {"value": "114", "label": "Armed forces/emergency service efficiency"},
                {"value": "115", "label": "Human rights/religious or racial harmony/equality or diversity"},
                {"value": "116", "label": "Recreation"},
                {"value": "117", "label": "Other charitable purposes"}
            ],
            className='bb-light-yellow'
        )
    ], "Cause")

def beneficiaries_filter():
    return filter_item([
        dcc.Dropdown(
            id='beneficiary-filter',
            multi=True,
            options=[
                {"value": "201", "label": "Children/young people"},
                {"value": "202", "label": "Elderly/old people"},
                {"value": "203", "label": "People with disabilities"},
                {"value": "204", "label": "People of a particular ethnic or racial origin"},
                {"value": "205", "label": "Other charities or voluntary bodies"},
                {"value": "206", "label": "Other defined groups"},
                {"value": "207", "label": "The general public/mankind"}
            ],
            className='bb-light-yellow'
        )
    ], "Beneficiaries")

def operation_filter():
    return filter_item([
        dcc.Dropdown(
            id='operation-filter',
            multi=True,
            options=[
                {"value": "301", "label": "Makes grants to individuals"},
                {"value": "302", "label": "Makes grants to organisations"},
                {"value": "303", "label": "Provides other finance"},
                {"value": "304", "label": "Provides human resources"},
                {"value": "305", "label": "Provides buildings/facilities/open space"},
                {"value": "306", "label": "Provides services"},
                {"value": "307", "label": "Provides advocacy/advice/information"},
                {"value": "308", "label": "Sponsors or undertakes research"},
                {"value": "309", "label": "Acts as an umbrella or resource body"},
                {"value": "310", "label": "Other charitable activities"}
            ],
            className='bb-light-yellow'
        )
    ], "Activity")

def max_countries_filter():
    return filter_item([
        'Ignore any charities that work in more than',
        html.Span(className='pb1', children=[
            dcc.Input(
                placeholder='Enter a value...',
                type='number',
                value='180',
                id='max-countries',
                className='mh1 w3 bb-light-yellow bg-inherit near-white pa1',
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
            values=[],
            id='include-dac',
            inputClassName='mr2',
        ),
        html.A(
            className='f6 i link light-gray underline',
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

import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt

from .tabs import output_tab
from .dashboard import financial_history_chart

def charitylist():
    return output_tab(
        label='Show charities',
        value='show-charities',
        children=[
            financial_history_chart(),
            datatable(),
        ]
    )

def download_tab():
    return output_tab(
        label='Download data',
        value='download-data',
        children=[
            download_link(),
            fields_to_include(),
        ]
    )


def datatable():
    return dt.DataTable(
        id='results-list',
        columns=[
            {"name": 'Charity Number',
             "id": "Charity Number"},
            {"name": 'Name', "id": "Name"},
            {"name": 'Income', "id": "Income"},
            {"name": 'Countries of operation',
             "id": "Countries of operation"}
        ],
        data=[],
        row_selectable='multi',
        style_as_list_view=True,
        style_table={
            # 'maxHeight': '500',
            'maxWidth': '100%',
        },
        style_cell={
            'minWidth': '0px',
            'maxWidth': '180px',
            'whiteSpace': 'normal',
        },
        # n_fixed_columns=1,
        # n_fixed_rows=1,
    )

def download_link():
    return html.Div(id='results-download-link', className='mv3 pv3', children=[])

def fields_to_include():
    return html.Div([
        html.H3('Fields to include in download', className='mv2 pa0'),
        html.P(
            "Charities will be included based on the criteria you have selected.",
            className="f6 gray i mt1"
        ),
        html.Div(className='cf mv3 flex flex-wrap', children=[
            html.Div(className='w-25', children=[
                html.H4('Charity information', className='mt3 mb0 pa0'),
                dcc.Checklist(
                    id='results-download-fields-main',
                    options=[
                        {'label': 'Charity number', 'value': 'ids.GB-CHC'},
                        {'label': 'Charity name', 'value': 'name'},
                        {'label': 'Governing document', 'value': 'governingDoc'},
                        {'label': 'Description of activities', 'value': 'activities'},
                        {'label': 'Charitable objects', 'value': 'objectives'},
                        {'label': 'Causes served', 'value': 'causes'},
                        {'label': 'Beneficiaries', 'value': 'beneficiaries'},
                        {'label': 'Activities', 'value': 'operations'},
                    ],
                    values=['ids.GB-CHC', 'name'],
                    labelClassName='db mv2',
                    inputClassName='mr2',
                    className='mt3',
                ),
            ]),
            html.Div(className='w-25', children=[
                html.H4('Financial', className='mt3 mb0 pa0'),
                dcc.Checklist(
                    id='results-download-fields-financial',
                    options=[
                        {'label': 'Latest income', 'value': 'income.latest.total'},
                        {'label': 'Company number', 'value': 'companiesHouseNumber'},
                        {'label': 'Financial year end', 'value': 'fyend'},
                        {'label': 'Number of trustees', 'value': 'people.trustees'},
                        {'label': 'Number of employees', 'value': 'people.employees'},
                        {'label': 'Number of volunteers', 'value': 'people.volunteers'},
                    ],
                    values=['income.latest.total'],
                    labelClassName='db mv2',
                    inputClassName='mr2',
                    className='mt3',
                ),
            ]),
            html.Div(className='w-25', children=[
                html.H4('Contact details', className='mt3 mb0 pa0'),
                dcc.Checklist(
                    id='results-download-fields-contact',
                    options=[
                        {'label': 'Email', 'value': 'contact.email'},
                        {'label': 'Address', 'value': 'contact.address'},
                        {'label': 'Postcode', 'value': 'contact.postcode'},
                        {'label': 'Phone number', 'value': 'contact.phone'},
                    ],
                    values=[],
                    labelClassName='db mv2',
                    inputClassName='mr2',
                    className='mt3',
                ),
            ]),
            html.Div(className='w-25', children=[
                html.H4('Geography fields', className='mt3 mb0 pa0'),
                dcc.Checklist(
                    id='results-download-fields-aoo',
                    options=[
                        {'label': 'Description of area of benefit', 'value': 'areaOfBenefit'},
                        {'label': 'Area of operation', 'value': 'areasOfOperation'},
                        {'label': 'Countries where this charity operates', 'value': 'countries'},
                    ],
                    values=[],
                    labelClassName='db mv2',
                    inputClassName='mr2',
                    className='mt3',
                ),
                html.P(
                    "The following fields are based on the postcode of the charities' UK registered office",
                    className="f6 gray i mt1"
                ),
                dcc.Checklist(
                    id='results-download-fields-geo',
                    options=[
                        {'label': 'Country', 'value': 'contact.geo.country'},
                        {'label': 'Region', 'value': 'contact.geo.region'},
                        {'label': 'County', 'value': 'contact.geo.admin_county'},
                        {'label': 'County [code]', 'value': "contact.geo.codes.admin_county"},
                        {'label': 'Local Authority', 'value': 'contact.geo.admin_district'},
                        {'label': 'Local Authority [code]', 'value': "contact.geo.codes.admin_district"},
                        {'label': 'Ward', 'value': 'contact.geo.admin_ward'},
                        {'label': 'Ward [code]', 'value': 'contact.geo.codes.admin_ward'},
                        {'label': 'Parish', 'value': 'contact.geo.parish'},
                        {'label': 'Parish [code]', 'value': 'contact.geo.codes.parish'},
                        {'label': 'LSOA', 'value': 'contact.geo.lsoa'},
                        {'label': 'MSOA', 'value': 'contact.geo.msoa'},
                        {'label': 'Parliamentary Constituency', 'value': 'contact.geo.parliamentary_constituency'},
                        {'label': 'Parliamentary Constituency [code]', 'value': 'contact.geo.codes.parliamentary_constituency'},
                    ],
                    values=[],
                    labelClassName='db mv2',
                    inputClassName='mr2',
                    className='mt3',
                ),
            ]),
        ])
    ])

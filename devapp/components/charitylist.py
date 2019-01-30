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
    return html.Div(id='results-download-link', className='', children=[])

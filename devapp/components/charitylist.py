import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt

from .tabs import TAB_STYLE, TAB_SELECTED_STYLE


def charitylist():
    return dcc.Tab(
        label='Data table',
        value='tab-2',
        className='',
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            datatable(),
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
    return html.A("Download data", id="results-download-link")

import dash_core_components as dcc
import dash_html_components as html

from .tabs import output_tab

def dashboard():
    return output_tab(
        label='Dashboard',
        value='dashboard',
        children=[
            financial_history_chart(),
            area_of_operation_map(),
        ]
    )

def financial_history_chart():
    return html.Div(
        className='w-100',
        children=[
            html.H3(
                "Financial history of charities"),
            html.P(
                "Figures given are in cash terms, without adjusting for inflation",
                className="f6 gray i mb2 mt0"
            ),
            dcc.RadioItems(
                options=[
                    {'label': 'Income',
                     'value': 'inc'},
                    {'label': 'Spending',
                     'value': 'exp'},
                ],
                value='inc',
                id="financial-history-type",
                labelClassName="pr2 f6",
                inputClassName="mr1 f6",
            ),
            html.Div(id="finances-chart",
                     className="h6")
        ]
    )

def area_of_operation_map():
    return html.Div(
        className='w-100',
        children=[
            html.H3("Where these charities work"),
            html.Div(id="area-of-operation-map",
                     className="h6")
        ]
    )

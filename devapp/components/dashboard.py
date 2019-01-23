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

def chart_wrapper(title, contents, caption=None):
    figcaption = [html.H3(title, className='pv2 ma0')]
    if isinstance(caption, list):
        figcaption += caption

    return html.Figure(
        className='w-100 mh0 mt0 mb3 pa2',
        style={'backgroundColor': '#444'},
        children=[
            html.Figcaption(figcaption),
            contents
        ]
    )

def financial_history_chart():
    return chart_wrapper(
        "Financial history of charities",
        html.Div(id="finances-chart",
                 className="h6 mw7"),
        [
            html.P(
                "Figures given are in cash terms, without adjusting for inflation",
                className="f6 gray i mb2 mt0"
            ),
            dcc.RadioItems(
                options=[
                    {'label': 'Income', 'value': 'inc'},
                    {'label': 'Spending', 'value': 'exp'},
                ],
                value='inc',
                id="financial-history-type",
                labelClassName="pr2 f6",
                inputClassName="mr1 f6",
            ),
        ]
    )

def area_of_operation_map():
    return chart_wrapper(
        "Where these charities work",
        html.Div(id="area-of-operation-map",
                    className="h6 mw7")
    )

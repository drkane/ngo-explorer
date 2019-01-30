import dash_core_components as dcc
import dash_html_components as html

from .tabs import output_tab

def dashboard():
    return output_tab(
        label='Dashboard',
        value='dashboard',
        children=[
            summary_numbers(),
            aggregate_financial_history_chart(),
            income_band_chart(),
            registered_region_chart(),
            area_of_operation_map(),
            classification_chart("Causes"),
            classification_chart("Beneficiaries"),
            classification_chart("Operations"),
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

def summary_numbers():
    return html.Div(
        id='summary-numbers',
        className='cf mb3 flex items-center',
    )

def aggregate_financial_history_chart():
    return chart_wrapper(
        "Income and spending of these charities",
        html.Div(id="aggregate-finances-chart",
                 className="h6 mw7"),
        [
            html.P(
                "Figures given are in cash terms, without adjusting for inflation",
                className="f6 gray i mb2 mt0"
            )
        ]
    )


def classification_chart(class_type):
    return chart_wrapper(
        "Charities by {}".format(class_type),
        html.Div(id="classification-{}-chart".format(class_type.lower()),
                 className="h6 mw7")
    )


def income_band_chart():
    return chart_wrapper(
        "Charities by income band",
        html.Div(id="income-band-chart",
                 className="h6 mw7")
    )


def registered_region_chart():
    return chart_wrapper(
        "Charities by region",
        html.Div(id="registered-region-chart",
                 className="h6 mw7"),
        [
            html.P(
                "Based on the postcode of the charities' UK registered office",
                className="f6 gray i mb2 mt0"
            ),
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

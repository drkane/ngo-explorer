import dash_core_components as dcc
import dash_html_components as html

def header():
    return html.Div(children=[
        html.H1(children=[
            'Development Charities Data Explorer',
            html.Span("alpha", className="gray f5 ml2 ttl")
        ], className='abril normal light-yellow pb3 bb b--gray ttu f2'),

        dcc.Markdown(children='''
An explorer for data on development charities based in the UK.
Uses data from the Charity Commission for England and Wales.
Powered by [CharityBase](https://charitybase.uk/).
    '''),
    ])

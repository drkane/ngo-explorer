import dash_core_components as dcc
import dash_html_components as html

def header():
    return html.Div(children=[
        html.H1(children=[
            'NGO Explorer',
            html.Span("alpha", className="gray f5 ml2 ttl")
        ], className='abril normal light-yellow ma0 ttu f2'),
        html.H2(children=[
            'Building networks across development NGOs',
        ], className='abril normal light-yellow ma0 f3'),

        dcc.Markdown(className='pt2', children='''
An explorer for data on development charities based in the UK.
Uses data from the Charity Commission for England and Wales.
Powered by [CharityBase](https://charitybase.uk/).'''),
        html.P(
            html.A(href='/about', children='About this tool'),
        )
    ], className='pb3 bb b--gray')

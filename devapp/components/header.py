import dash_core_components as dcc
import dash_html_components as html

def header():
    return html.Div(
        className='pb4 bb b--gray mv4 cf',
        children=[
            html.Div(
                className='fl w-50',
                children=[
                    html.H1(
                        className='abril normal ma0 ttu f2',
                        children=[
                            'NGO Explorer',
                            html.Span("alpha", className="gray f5 ml2 ttl")
                        ]
                    ),
                    html.H2(
                        className='abril normal ma0 f3',
                        children=[
                            'Building networks across development NGOs',
                        ]
                    ),
                ]
            ),
            dcc.Markdown(
                className='fl w-third mid-gray',
                children='''
An explorer for data on development charities based in the UK.
Uses data from the Charity Commission for England and Wales.
Powered by [CharityBase](https://charitybase.uk/). [About this tool](/about)'''
            ),
        ]
    )

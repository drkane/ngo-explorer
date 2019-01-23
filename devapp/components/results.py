import dash_html_components as html

from .dashboard import dashboard
from .charitylist import charitylist, download_tab
from .tabs import output_tab_container

def results():
    return [
        html.H2(id='results-count'),
        html.Div(
            className="dn w-100",
            id="results-container",
            children=[
                output_tab_container(
                    id="tabs",
                    value='dashboard',
                    children=[
                        dashboard(),
                        charitylist(),
                        download_tab(),
                    ]
                ),
            ]
        ),
    ]

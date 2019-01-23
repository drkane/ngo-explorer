import dash_core_components as dcc
import dash_html_components as html

from .dashboard import dashboard
from .charitylist import charitylist
from .tabs import TABS_CONTAINER_STYLE

def results():
    return [
        html.H2(id='results-count'),
        html.Div(
            className="dn w-100",
            id="results-container",
            children=[
                dcc.Tabs(
                    id="tabs",
                    value='tab-1',
                    className='',
                    style=TABS_CONTAINER_STYLE,
                    children=[
                        dashboard(),
                        charitylist(),
                    ]
                ),
            ]
        ),
    ]

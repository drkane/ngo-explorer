import dash_core_components as dcc

TABS_CONTAINER_STYLE = {
    'borderBottom': '2px solid #FBF1A9',
    'marginBottom': '16px',
}
TAB_STYLE = {
    'width': 'auto',
    'marginRight': '8px',
    'padding': '8px',
    'fontSize': '1.25rem',
    'color':  '#f4f4f4',
    'backgroundColor': 'inherit',
    'borderTop': '1px solid gray',
    'borderLeft': '1px solid gray',
    'borderRight': '1px solid gray',
    'borderBottom': '1px solid gray',
}
TAB_SELECTED_STYLE = {
    'width': 'auto',
    'margin-right': '8px',
    'padding': '8px',
    'fontSize': '1.25rem',
    'color':  '#111',
    'backgroundColor': '#FBF1A9',
    'borderTop': '0px solid gray',
    'borderLeft': '0px solid gray',
    'borderRight': '0px solid gray',
    'borderBottom': '0px solid gray',
}


def output_tab(**kwargs):
    return dcc.Tab(
        className='',
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        **kwargs
    )

def output_tab_container(**kwargs):
    return dcc.Tabs(
        className='',
        style=TABS_CONTAINER_STYLE,
        **kwargs
    )

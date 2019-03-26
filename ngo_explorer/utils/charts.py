import copy
import uuid
from collections import Counter
import re

from flask import current_app
from flask_babel import ngettext
import plotly.graph_objs as go
import plotly
from requests.compat import json as _json

from .filters import CLASSIFICATION
from .utils import get_scaling_factor
from .countries import get_country_by_id

LAYOUT = {
    'yaxis': {
        'automargin': True,
        'visible': False,
        'showgrid': False,
        'showline': False,
        'linewidth': 0,
        'rangemode': 'tozero',
        'fixedrange': True,
        'tickfont': {
            # 'size': 20
        },
    },
    'xaxis': {
        'automargin': True,
        'showgrid': False,
        'showline': False,
        'rangemode': 'tozero',
        'fixedrange': True,
        'linewidth': 0,
        'tickfont': {
            # 'size': 20
        },
    },
    'margin': go.layout.Margin(
        l=40,
        r=24,
        b=40,
        t=24,
        pad=4
    ),
    'clickmode': 'event+select',
    'dragmode': False,
    'paper_bgcolor': 'rgba(1, 1, 1, 0.0)',
    'plot_bgcolor': 'rgba(1, 1, 1, 0.0)',
}
H_LAYOUT = {
    'xaxis': copy.deepcopy(LAYOUT['yaxis']),
    'yaxis': copy.deepcopy(LAYOUT['xaxis']),
    **{
        k: copy.deepcopy(v) for k, v in LAYOUT.items() if k not in ['xaxis', 'yaxis']
    }
}


def location_map(countries, continents=None, height=200, landcolor="rgb(229, 229, 229)", static=False):
    continents = continents if continents else list(
        set([c["continent"] for c in countries]))
    scope = 'world'
    if len(continents) == 1 and continents[0].lower() in current_app.config["PLOTLY_GEO_SCOPES"]:
        scope = continents[0].lower()

    return plotly.offline.plot({
        "data": [
            go.Scattergeo(
                lon=[c['longitude'] for c in countries],
                lat=[c['latitude'] for c in countries],
                text=["{} ({:,.0f} charit{})".format(
                    c['name'],
                    c.get("charity_count", 0),
                    "y" if c.get("charity_count", 0) ==1 else "ies"
                 ) for c in countries],
                hoverinfo="text",
                marker=dict(
                    size=6,
                    color='#237756',
                    symbol='circle',
                    opacity=1,
                ),
            ),
            go.Choropleth(
                locationmode='ISO-3',
                locations=[c['iso'] for c in countries],
                z=[1 for c in countries],
                text=["{} ({})".format(
                    c['name'],
                    ngettext("%(num)d charity", "%(num)d charities", num=c.get("charity_count", 0)),
                ) for c in countries],
                colorscale=[[0, '#237756'], [1, '#237756']],
                autocolorscale=False,
                showscale=False,
                hoverinfo="text",
                marker=dict(
                    line=dict(
                        width=1,
                        color='#1e6c4d',
                    ),
                ),
            ),
        ],
        "layout": dict(
            geo=dict(
                scope=scope,
                showframe=False,
                showland=True,
                showcoastlines=False,
                landcolor=landcolor,
                showcountries=False,
                bgcolor='rgba(255, 255, 255, 0.0)',
                projection=dict(
                    type='natural earth'
                ) if scope != 'world' else {},
            ),
            dragmode=False,
            margin=dict(l=0, r=0, t=0, b=0),
            height=height,
        ),
    }, output_type='div', include_plotlyjs=False, config=dict(
        displayModeBar=False,
        staticPlot=static,
        scrollZoom=False,
    ))


def horizontal_bar(categories, value="count", text=None, log_axis=False, **kwargs):

    # categories = {
    #   "name": "category name"
    #   ...various values
    # }

    if not categories:
        return dict(
            data=[],
            layout={},
        )

    hb_plot = plotly.tools.make_subplots(
        rows=len(categories),
        cols=1,
        subplot_titles=[x["name"] for x in categories],
        shared_xaxes=True,
        print_grid=False,
        vertical_spacing=(0.45 / len(categories)),
        **kwargs
    )
    for k, x in enumerate(categories):
        hb_plot.append_trace(dict(
            type='scatter',
            mode='lines+markers',
            y=[x["name"], x["name"]],
            x=[x[value], 0],
            text=[x.get(text, "{:,.0f}".format(x[value])), ""],
            hoverinfo='text',
            hoverlabel=dict(
                bgcolor='#237756',
                bordercolor='#237756',
                font=dict(
                    color='#fff',
                ),
            ),
            line=dict(
                color='#237756',
                width=6,
            ),
            marker=dict(
                color='#fff',
                symbol='circle',
                size=16,
                line=dict(
                    width=6,
                    color='#237756',
                ),
                maxdisplayed=1,
            ),

        ), k+1, 1)

    hb_plot['layout'].update(
        showlegend=False,
        **{
            k: copy.deepcopy(v) for k, v in LAYOUT.items() if k not in ['xaxis', 'yaxis']
        }
    )

    for x in hb_plot["layout"]['annotations']:
        x['x'] = 0
        x['xanchor'] = 'left'
        x['font'] = dict(
            size=12,
        )

    for x in hb_plot['layout']:
        if x.startswith('yaxis') or x.startswith('xaxis'):
            hb_plot['layout'][x]['visible'] = False

    if log_axis:
        hb_plot['layout']['xaxis']['type'] = 'log'

    hb_plot['layout']['margin']['l'] = 0
    height_calc = 55 * len(categories)
    height_calc = max([height_calc, 350])
    hb_plot['layout']['height'] = height_calc

    return dict(
        data=hb_plot.to_dict().get('data', []),
        layout=hb_plot.to_dict().get('layout', {}),
        id=str(uuid.uuid4()).replace("-", "_"),
    )

def plotly_json(data):
    return _json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)


def word_cloud(charity_data):
    stop_words = [
        # from https://gist.github.com/sebleier/554280
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
        "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its",
        "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom",
        "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but",
        "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against",
        "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up",
        "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
        "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most",
        "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
        "s", "t", "can", "will", "just", "don", "should", "now",
        # others
        "throughout", "around", "charity", "charitable",
    ]
    alpha_regex = r'[^a-zA-Z]+'

    words = Counter()
    for c in charity_data:
        if not getattr(c, "activities", ""):
            continue
        a = getattr(c, "activities", "").split()
        for word in a:
            word = re.sub(alpha_regex, '', word.lower())
            if word in stop_words or len(word) <=3:
                continue
            words.update([word])

    return dict(words.most_common(50))


def line_chart(data):

    chart_data = []
    for d in data:
        chart_data.append(go.Scatter(
            **d
        ))

    layout = copy.deepcopy(LAYOUT)
    layout["yaxis"]["rangemode"] = 'tozero'
    # layout["yaxis"]["autorange"] = True
    layout["yaxis"]["visible"] = True

    return dict(
        data=chart_data,
        layout=layout,
        id=str(uuid.uuid4()).replace("-", "_"),
    )

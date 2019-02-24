import copy
import uuid
from collections import Counter
import re

from flask import current_app
import plotly.graph_objs as go
import plotly
from requests.compat import json as _json

from .filters import CLASSIFICATION
from .utils import get_scaling_factor

LAYOUT = {
    'yaxis': {
        'automargin': True,
        'visible': False,
        'showgrid': False,
        'showline': False,
        'linewidth': 0,
        'rangemode': 'tozero',
        'tickfont': {
            # 'size': 20
        },
    },
    'xaxis': {
        'automargin': True,
        'showgrid': False,
        'showline': False,
        'rangemode': 'tozero',
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
    'dragmode': 'select',
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

def get_charts(data):

    for i in CLASSIFICATION.keys():
        for x in data["aggregate"][i]["buckets"]:
            x['name'] = CLASSIFICATION.get(i, {}).get(x["id"], x["id"])

    income_buckets = parse_income_buckets(
        data["aggregate"]["income"]["buckets"]
    )

    return {
        "buckets": income_buckets,
        "count": horizontal_bar(income_buckets, "count"),
        "amount": horizontal_bar(income_buckets, "sumIncome", "sumIncomeText", log_axis=True),
        **{
            k: horizontal_bar(data["aggregate"][k]["buckets"], "count")
            for k in CLASSIFICATION.keys()
        },
        "word_cloud": word_cloud(data["list"]),
    }


def location_map(countries, continents=None, height=200, landcolor="rgb(229, 229, 229)"):
    continents = continents if continents else list(
        set([c["continent"] for c in countries]))
    scope = 'world'
    if len(continents) == 1 and continents[0].lower() in current_app.config["PLOTLY_GEO_SCOPES"]:
        scope = continents[0].lower()

    return plotly.offline.plot({
        "data": [
            go.Scattergeo(
                locationmode='ISO-3',
                locations=[c['iso'] for c in countries],
                text=[c['name'] for c in countries],
                hoverinfo="none",
                marker=dict(
                    size=6,
                    color='rgb(0, 0, 0)',
                    symbol='circle-dot',
                    opacity=1,
                ),
            ),
            go.Choropleth(
                locationmode='ISO-3',
                locations=[c['iso'] for c in countries],
                z=[1 for c in countries],
                text=[c['name'] for c in countries],
                colorscale=[[0, 'rgb(0, 0, 0)'], [1, 'rgb(0, 0, 0)']],
                autocolorscale=False,
                showscale=False,
                hoverinfo="text",
                marker=dict(
                    line=dict(
                        width=1,
                        color='rgb(50, 50, 50)',
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
            margin=dict(l=0, r=0, t=0, b=0),
            height=height,
        ),
    }, output_type='div', include_plotlyjs=False, config=dict(
        displayModeBar=False,
        staticPlot=True,
    ))


def horizontal_bar(categories, value="count", text=None, log_axis=False):

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
        vertical_spacing=0.05,
        print_grid=False,
    )
    for k, x in enumerate(categories):
        hb_plot.append_trace(dict(
            type='bar',
            orientation='h',
            y=[x["name"]],
            x=[x[value]],
            text=[x.get(text, "{:,.0f}".format(x[value]))],
            textposition='auto',
            constraintext='both',
            hoverinfo='y',
            marker=dict(
                color='rgb(31,119,180)',
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
    height_calc = 65 * len(categories)
    height_calc = min(height_calc, 650)
    height_calc = max(height_calc, 450)
    hb_plot['layout']['height'] = height_calc

    return dict(
        data=hb_plot.to_dict().get('data', []),
        layout=hb_plot.to_dict().get('layout', {}),
        id=str(uuid.uuid4()).replace("-", "_"),
    )

def plotly_json(data):
    return _json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)


def parse_income_buckets(income_buckets: list):

    new_bucket_labels = {
        "Min. £1": "Under £10k",
        "Min. £3": "Under £10k",
        "Min. £10": "Under £10k",
        "Min. £32": "Under £10k",
        "Min. £100": "Under £10k",
        "Min. £316": "Under £10k",
        "Min. £1000": "Under £10k",
        "Min. £3162": "Under £10k",
        "Min. £10000": "£10k-£100k",
        "Min. £31623": "£10k-£100k",
        "Min. £100000": "£100k-£1m",
        "Min. £316228": "£100k-£1m",
        "Min. £1000000": "£1m-£10m",
        "Min. £3162278": "£1m-£10m",
        "Min. £10000000": "Over £10m",
        "Min. £31622777": "Over £10m",
        "Min. £100000000": "Over £10m",
        "Min. £316227766": "Over £10m",
        "Min. £1000000000": "Over £10m",
    }

    # merge all the buckets into one
    new_buckets = {}
    for i in income_buckets:
        id_ = new_bucket_labels.get(i["name"], i["id"])
        if id_ not in new_buckets:
            new_buckets[id_] = copy.copy(i)
            new_buckets[id_]["name"] = id_
        else:
            new_buckets[id_]["count"] += i["count"]
            new_buckets[id_]["sumIncome"] += i["sumIncome"]

    # scale the money amounts and add a text representation
    income_buckets = []
    for i in new_buckets.values():
        scale = get_scaling_factor(i["sumIncome"])
        i["sumIncomeText"] = "£" + scale[2].format(i["sumIncome"] / scale[0])
        income_buckets.append(i)

    return income_buckets

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
        "throughout", "around",
    ]
    alpha_regex = r'[^a-zA-Z]+'

    words = Counter()
    for c in charity_data:
        if not c.get("activities", ""):
            continue
        a = c.get("activities", "").split()
        for word in a:
            word = re.sub(alpha_regex, '', word.lower())
            if word in stop_words or len(word) <=3:
                continue
            words.update([word])

    return dict(words.most_common(50))

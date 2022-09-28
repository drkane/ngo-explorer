import copy
import math
import re
import uuid
from collections import Counter

import plotly
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from flask import current_app, url_for
from flask_babel import ngettext
from requests.compat import json as _json

from .countries import get_country_by_id
from .filters import CLASSIFICATION
from .utils import get_scaling_factor

LAYOUT = {
    "yaxis": {
        "automargin": True,
        "visible": False,
        "showgrid": False,
        "showline": False,
        "linewidth": 0,
        "rangemode": "tozero",
        "fixedrange": True,
        "tickfont": {
            # 'size': 20
        },
    },
    "xaxis": {
        "automargin": True,
        "showgrid": False,
        "showline": False,
        "rangemode": "tozero",
        "autorange": True,
        "linewidth": 0,
        "tickfont": {
            # 'size': 20
        },
    },
    "margin": go.layout.Margin(l=40, r=24, b=40, t=24, pad=4),
    "clickmode": "event+select",
    "dragmode": False,
    "paper_bgcolor": "rgba(1, 1, 1, 0.0)",
    "plot_bgcolor": "rgba(1, 1, 1, 0.0)",
}
H_LAYOUT = {
    "xaxis": copy.deepcopy(LAYOUT["yaxis"]),
    "yaxis": copy.deepcopy(LAYOUT["xaxis"]),
    **{k: copy.deepcopy(v) for k, v in LAYOUT.items() if k not in ["xaxis", "yaxis"]},
}


def location_map(
    countries, continents=None, height=200, landcolor="rgb(229, 229, 229)", static=False
):
    continents = (
        continents if continents else list(set([c["continent"] for c in countries]))
    )
    scope = "world"
    if (
        len(continents) == 1
        and continents[0].lower() in current_app.config["PLOTLY_GEO_SCOPES"]
    ):
        scope = continents[0].lower()

    filtered = False
    for c in countries:
        if c.get("filtered"):
            filtered = True
            break
    if filtered:
        countries = [c for c in countries if c.get("filtered")]

    return plotly.offline.plot(
        {
            "data": [
                go.Scattergeo(
                    lon=[c["longitude"] for c in countries],
                    lat=[c["latitude"] for c in countries],
                    text=[
                        "{} ({:,.0f} charit{})".format(
                            c["name"],
                            c.get("count", 0),
                            "y" if c.get("count", 0) == 1 else "ies",
                        )
                        for c in countries
                    ],
                    hoverinfo="text",
                    marker=dict(
                        size=6,
                        color=[c.get("count", 1) for c in countries],
                        colorscale=[[0, "#0ca777"], [1, "#237756"]],
                        autocolorscale=False,
                        symbol="circle",
                        opacity=1,
                    ),
                ),
                go.Choropleth(
                    locationmode="ISO-3",
                    locations=[c["iso"] for c in countries],
                    z=[c.get("count", 1) for c in countries],
                    text=[
                        "{} ({})".format(
                            c["name"],
                            ngettext(
                                "%(num)d charity",
                                "%(num)d charities",
                                num=c.get("count", 0),
                            ),
                        )
                        for c in countries
                    ],
                    colorscale=[[0, "#0ca777"], [1, "#237756"]],
                    autocolorscale=False,
                    showscale=False,
                    hoverinfo="text",
                    marker=dict(
                        line=dict(
                            width=0,
                            color="#1e6c4d",
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
                    bgcolor="rgba(255, 255, 255, 0.0)",
                    projection=dict(type="natural earth") if scope != "world" else {},
                ),
                dragmode=False,
                margin=dict(l=0, r=0, t=0, b=0),
                height=height,
            ),
        },
        output_type="div",
        include_plotlyjs=False,
        config=dict(
            displayModeBar=False,
            staticPlot=static,
            scrollZoom=False,
            topojsonURL=url_for("static", filename="maps/"),
        ),
    )


def horizontal_bar(
    categories, value="count", text=None, log_axis=False, colour="#237756", **kwargs
):

    # categories = {
    #   "name": "category name"
    #   ...various values
    # }

    if not categories:
        return dict(
            data=[],
            layout={},
        )

    hb_plot = make_subplots(
        rows=len(categories),
        cols=1,
        subplot_titles=[x["name"] for x in categories],
        shared_xaxes=True,
        print_grid=False,
        vertical_spacing=(0.45 / len(categories)),
        **kwargs
    )
    max_value = max([x[value] for x in categories])
    for k, x in enumerate(categories):
        hb_plot.add_trace(
            dict(
                type="bar",
                orientation="h",
                y=[x["name"]],
                x=[x[value]],
                text=[x.get(text, "{:,.0f}".format(x[value]))],
                hoverinfo="text",
                hoverlabel=dict(
                    bgcolor=colour,
                    bordercolor=colour,
                    font=dict(
                        color="#fff",
                    ),
                ),
                textposition="auto"
                if not log_axis or not max_value or ((x[value] / max_value) > 0.05)
                else "outside",
                marker=dict(
                    color=colour,
                ),
            ),
            k + 1,
            1,
        )

    hb_plot["layout"].update(
        showlegend=False,
        **{
            k: copy.deepcopy(v)
            for k, v in LAYOUT.items()
            if k not in ["xaxis", "yaxis"]
        }
    )

    for x in hb_plot["layout"]["annotations"]:
        x["x"] = 0
        x["xanchor"] = "left"
        x["align"] = "left"
        x["font"] = dict(
            size=10,
        )

    for x in hb_plot["layout"]:
        if x.startswith("yaxis") or x.startswith("xaxis"):
            hb_plot["layout"][x]["visible"] = False

        if x.startswith("xaxis"):
            if log_axis:
                hb_plot["layout"][x]["type"] = "log"
                hb_plot["layout"][x]["range"] = [1, int(math.log10(max_value)) + 1]
            else:
                hb_plot["layout"][x]["range"] = [0, max_value * 1.1]

    hb_plot["layout"]["margin"]["l"] = 0
    height_calc = 55 * len(categories)
    height_calc = max([height_calc, 350])
    hb_plot["layout"]["height"] = height_calc

    return dict(
        data=hb_plot.to_dict().get("data", []),
        layout=hb_plot.to_dict().get("layout", {}),
        id=str(uuid.uuid4()).replace("-", "_"),
    )


def plotly_json(data):
    return _json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)


def word_cloud(charity_data):
    stop_words = [
        # from https://gist.github.com/sebleier/554280
        "i",
        "me",
        "my",
        "myself",
        "we",
        "our",
        "ours",
        "ourselves",
        "you",
        "your",
        "yours",
        "yourself",
        "yourselves",
        "he",
        "him",
        "his",
        "himself",
        "she",
        "her",
        "hers",
        "herself",
        "it",
        "its",
        "itself",
        "they",
        "them",
        "their",
        "theirs",
        "themselves",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "these",
        "those",
        "am",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "having",
        "do",
        "does",
        "did",
        "doing",
        "a",
        "an",
        "the",
        "and",
        "but",
        "if",
        "or",
        "because",
        "as",
        "until",
        "while",
        "of",
        "at",
        "by",
        "for",
        "with",
        "about",
        "against",
        "between",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "to",
        "from",
        "up",
        "down",
        "in",
        "out",
        "on",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "any",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "s",
        "t",
        "can",
        "will",
        "just",
        "don",
        "should",
        "now",
        # others
        "throughout",
        "around",
        "charity",
        "charitable",
    ]
    alpha_regex = r"[^a-zA-Z]+"

    words = Counter()
    for c in charity_data:
        if not getattr(c, "activities", ""):
            continue
        a = getattr(c, "activities", "").split()
        for word in a:
            word = re.sub(alpha_regex, "", word.lower())
            if word in stop_words or len(word) <= 3:
                continue
            words.update([word])

    return dict(words.most_common(50))


def line_chart(data):

    chart_data = []
    for d in data:
        chart_data.append(go.Scatter(**d))

    layout = copy.deepcopy(LAYOUT)
    layout["yaxis"]["rangemode"] = "tozero"
    # layout["yaxis"]["autorange"] = True
    layout["yaxis"]["visible"] = True

    return dict(
        data=chart_data,
        layout=layout,
        id=str(uuid.uuid4()).replace("-", "_"),
    )

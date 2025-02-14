import copy
import json
import math
import uuid
from typing import Optional

import plotly
import plotly.graph_objs as go
from flask import current_app, url_for
from flask_babel import ngettext
from plotly.subplots import make_subplots

from ngo_explorer.classes.charts import ChartData, ChartValue
from ngo_explorer.classes.countries import Country
from ngo_explorer.classes.results import ResultBucket

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
    countries: list[Country],
    continents: list[str] = [],
    height: int = 200,
    landcolor: str = "rgb(229, 229, 229)",
    static: bool = False,
):
    continents = (
        continents if continents else list(set([c.continent for c in countries]))
    )
    scope = "world"
    if (
        len(continents) == 1
        and continents[0].lower() in current_app.config["PLOTLY_GEO_SCOPES"]
    ):
        scope = continents[0].lower()

    filtered = False
    for c in countries:
        if c.filtered:
            filtered = True
            break
    if filtered:
        countries = [c for c in countries if c.filtered]

    return plotly.offline.plot(
        {
            "data": [
                go.Scattergeo(
                    lon=[c.longitude for c in countries],
                    lat=[c.latitude for c in countries],
                    text=[
                        "{} ({})".format(
                            c.name,
                            ngettext(
                                "%(num)d charity",
                                "%(num)d charities",
                                num=c.count,
                            ),
                        )
                        if c.count
                        else c.name
                        for c in countries
                    ],
                    hoverinfo="text",
                    marker=dict(
                        size=6,
                        color=[c.count or 1 for c in countries],
                        colorscale=[[0, "#0ca777"], [1, "#237756"]],
                        autocolorscale=False,
                        symbol="circle",
                        opacity=1,
                    ),
                ),
                go.Choropleth(
                    locationmode="ISO-3",
                    locations=[c.iso for c in countries],
                    z=[c.count or 1 for c in countries],
                    text=[
                        "{} ({})".format(
                            c.name,
                            ngettext(
                                "%(num)d charity",
                                "%(num)d charities",
                                num=c.count,
                            ),
                        )
                        if c.count
                        else c.name
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
    categories: list[ResultBucket],
    value: ChartValue = "count",
    text: Optional[str] = None,
    log_axis: bool = False,
    colour: str = "#237756",
    **kwargs,
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
        subplot_titles=[x.name for x in categories],
        shared_xaxes=True,
        print_grid=False,
        vertical_spacing=(0.45 / len(categories)),
        **kwargs,
    )
    max_value = max(
        [
            getattr(x, value)
            for x in categories
            if isinstance(getattr(x, value), (int, float))
        ]
    )
    for k, x in enumerate(categories):
        value_ = getattr(x, value)
        if value_ is None:
            continue
        text_ = "{:,.0f}".format(value_)
        if text:
            text_ = getattr(x, text, text_)
        hb_plot.add_trace(
            go.Bar(
                type="bar",
                orientation="h",
                y=[x.name],
                x=[value_],
                text=[text_],
                hoverinfo="text",
                hoverlabel=dict(
                    bgcolor=colour,
                    bordercolor=colour,
                    font=dict(
                        color="#fff",
                    ),
                ),
                textposition=(
                    "auto"
                    if not log_axis or not max_value or ((value_ / max_value) > 0.05)
                    else "outside"
                ),
                marker=dict(
                    color=colour,
                ),
            ),
            k + 1,
            1,
        )

    assert isinstance(hb_plot.layout, go.Layout)
    hb_plot.layout.update(
        showlegend=False,
        **{
            k: copy.deepcopy(v)
            for k, v in LAYOUT.items()
            if k not in ["xaxis", "yaxis"]
        },
    )

    assert isinstance(hb_plot.layout.annotations, tuple)
    for annotation in hb_plot.layout.annotations:
        assert isinstance(annotation, go.layout.Annotation)
        annotation["x"] = 0
        annotation["xanchor"] = "left"
        annotation["align"] = "left"
        annotation["font"] = dict(
            size=10,
        )

    for x in hb_plot.layout:
        if x.startswith("yaxis") or x.startswith("xaxis"):
            hb_plot.layout[x]["visible"] = False  # type: ignore

        if x.startswith("xaxis"):
            if log_axis:
                hb_plot.layout[x]["type"] = "log"  # type: ignore
                hb_plot.layout[x]["range"] = [1, int(math.log10(max_value)) + 1]  # type: ignore
            else:
                hb_plot.layout[x]["range"] = [0, max_value * 1.1]  # type: ignore

    hb_plot.layout["margin"]["l"] = 0  # type: ignore
    height_calc = 55 * len(categories)
    height_calc = max([height_calc, 350])
    hb_plot.layout["height"] = height_calc

    return dict(
        data=hb_plot.to_dict().get("data", []),
        layout=hb_plot.to_dict().get("layout", {}),
        id=str(uuid.uuid4()).replace("-", "_"),
    )


def plotly_json(data):
    return json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)


def line_chart(data: list[go.Scatter]) -> ChartData:
    layout = copy.deepcopy(LAYOUT)
    layout["yaxis"]["rangemode"] = "tozero"
    # layout["yaxis"]["autorange"] = True
    layout["yaxis"]["visible"] = True

    return ChartData(
        data=data,
        layout=layout,
        id=str(uuid.uuid4()).replace("-", "_"),
    )

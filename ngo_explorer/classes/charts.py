from typing import Literal, TypedDict

import plotly.graph_objs as go


class ChartData(TypedDict):
    data: list[go.Scatter]
    layout: dict
    id: str


ChartValue = Literal["count", "sum", "sumIncome"]

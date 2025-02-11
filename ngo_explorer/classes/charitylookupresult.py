import copy
from dataclasses import InitVar, asdict, dataclass, fields
from typing import Optional

from flask_babel import _

from ngo_explorer.classes.charitylookupcharity import CharityLookupCharity
from ngo_explorer.utils.charts import horizontal_bar, word_cloud
from ngo_explorer.utils.countries import get_country_by_id
from ngo_explorer.utils.filters import CLASSIFICATION
from ngo_explorer.utils.utils import get_scaling_factor


@dataclass
class ResultBucket:
    key: str
    count: int
    name: Optional[str] = None
    sum: Optional[int] = None
    sumIncomeText: Optional[str] = None


@dataclass
class ResultAggregateFinances:
    latestSpending: list[ResultBucket] = []


@dataclass
class ResultAggregateGeo:
    region: list[ResultBucket] = []
    country: list[ResultBucket] = []


@dataclass
class ResultAggregate:
    finances: ResultAggregateFinances = ResultAggregateFinances()
    causes: list[ResultBucket] = []
    beneficiaries: list[ResultBucket] = []
    operations: list[ResultBucket] = []
    areas: list[ResultBucket] = []
    geo: ResultAggregateGeo = ResultAggregateGeo()


@dataclass
class CharityLookupResult:
    aggregate: Optional[ResultAggregate] = None
    count: int = 0
    list_: Optional[list[CharityLookupCharity]] = None
    inflation: InitVar[Optional[dict[str, float]]] = None

    def __post_init__(self, inflation: Optional[dict[str, float]] = None):
        self._parse_aggregates()
        self._parse_income_buckets()

    def _parse_aggregates(self):
        if not self.aggregate:
            return

        if self.aggregate.areas:
            self.countries = [
                {"count": i.count, **get_country_by_id(i.key), "id": i.key}
                for i in self.aggregate.areas
                if get_country_by_id(i.key)
            ]
        else:
            self.countries = []

        if self.aggregate.finances.latestSpending:
            self.total_income = sum(
                [f["sum"] for f in self.aggregate.finances.latestSpending]
            )
            scale = get_scaling_factor(self.total_income)
            self.total_income_text = "£" + scale[2].format(self.total_income / scale[0])
            self.total_income_years = {}
            if self.list_:
                for c in self.list_:
                    if c.finances and c.finances[0].financialYear.end:
                        year = c.finances[0].financialYear.end.year
                        if year not in self.total_income_years:
                            self.total_income_years[year] = 0
                        self.total_income_years[year] += 1

    def _parse_income_buckets(self):
        if not self.aggregate:
            return
        income_buckets = self.aggregate.finances.latestSpending
        if not income_buckets:
            return

        new_bucket_labels = {
            "Min. £1": _("Under £10k"),
            "Min. £3": _("Under £10k"),
            "Min. £10": _("Under £10k"),
            "Min. £32": _("Under £10k"),
            "Min. £100": _("Under £10k"),
            "Min. £316": _("Under £10k"),
            "Min. £1000": _("Under £10k"),
            "Min. £3162": _("Under £10k"),
            "Min. £10000": _("£10k-£100k"),
            "Min. £31623": _("£10k-£100k"),
            "Min. £100000": _("£100k-£1m"),
            "Min. £316228": _("£100k-£1m"),
            "Min. £1000000": _("£1m-£10m"),
            "Min. £3162278": _("£1m-£10m"),
            "Min. £10000000": _("Over £10m"),
            "Min. £31622777": _("Over £10m"),
            "Min. £100000000": _("Over £10m"),
            "Min. £316227766": _("Over £10m"),
            "Min. £1000000000": _("Over £10m"),
        }

        # merge all the buckets into one
        new_buckets = {}
        for i in income_buckets:
            id_ = new_bucket_labels.get(i.name or i.key, i.key)
            if id_ not in new_buckets:
                new_buckets[id_] = asdict(i)
                new_buckets[id_]["name"] = id_
            else:
                new_buckets[id_]["count"] += i.count
                new_buckets[id_]["sum"] += i.sum

        # scale the money amounts and add a text representation
        income_buckets: list[ResultBucket] = []
        for i in new_buckets.values():
            scale = get_scaling_factor(i["sum"])
            i["sumIncomeText"] = "£" + scale[2].format(i["sum"] / scale[0])
            income_buckets.append(
                ResultBucket(
                    key=i["key"],
                    count=i["count"],
                    name=i["name"],
                    sum=i["sum"],
                    sumIncomeText=i["sumIncomeText"],
                )
            )

        self.aggregate.finances.latestSpending = income_buckets

    def get_charity(self):
        if len(self.list_):
            return self.list_[0]

    def set_charts(self, selected_countries=None):
        self.charts = self.get_charts(selected_countries)

    def get_charts(self, selected_countries=None):
        if not self.aggregate:
            return None

        for i in CLASSIFICATION.keys():
            for x in getattr(self.aggregate, i):
                x.name = CLASSIFICATION.get(i, {}).get(x["key"], x["key"])

        if selected_countries and len(selected_countries) == 1:
            selected_country = selected_countries[0]["id"]
            countries = [c for c in self.countries if c["id"] != selected_country]
        else:
            countries = self.countries

        colours = ["#237756", "#F9AF42", "#043942", "#0CA777"]

        return {
            "count": horizontal_bar(
                self.aggregate.finances.latestSpending, "count", colour=colours[0]
            ),
            "amount": horizontal_bar(
                self.aggregate.finances.latestSpending,
                "sum",
                "sumIncomeText",
                log_axis=True,
                colour=colours[1],
            ),
            "countries": horizontal_bar(countries[0:12], "count", colour=colours[2]),
            **{
                k: horizontal_bar(
                    getattr(self.aggregate, k), "count", colour=colours[i]
                )
                for i, k in enumerate(CLASSIFICATION.keys())
            },
            "word_cloud": word_cloud(self.list_),
        }

import dataclasses
from dataclasses import dataclass, field
from typing import Optional
from warnings import warn

from flask_babel import _

from ngo_explorer.classes.charity import Charity
from ngo_explorer.classes.countries import Country
from ngo_explorer.classes.results import ResultAggregate
from ngo_explorer.utils.charts import horizontal_bar
from ngo_explorer.utils.countries import get_country_by_id
from ngo_explorer.utils.filters import CLASSIFICATION
from ngo_explorer.utils.utils import get_scaling_factor
from ngo_explorer.utils.word_cloud import word_cloud


@dataclass
class Result:
    aggregate: Optional[ResultAggregate] = None
    count: int = 0
    list_: Optional[list[Charity]] = None
    countries: list[Country] = field(default_factory=list)

    def __post_init__(self):
        self._parse_aggregates()
        self._parse_income_buckets()

    def _parse_aggregates(self):
        if not self.aggregate:
            return

        if self.aggregate.areas:
            for i in self.aggregate.areas:
                country = get_country_by_id(i.key)
                if not country:
                    continue
                self.countries.append(dataclasses.replace(country, count=i.count))

        if self.aggregate.finances.latestSpending:
            self.total_income = sum(
                [f.sum for f in self.aggregate.finances.latestSpending if f.sum]
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
        if not self.aggregate.finances.latestSpending:
            return

        new_bucket_labels = {
            "Under £10k": _("Under £10k"),
            "£10k-£100k": _("£10k-£100k"),
            "£100k-£1m": _("£100k-£1m"),
            "£1m-£10m": _("£1m-£10m"),
            "Over £10m": _("Over £10m"),
        }

        for i in self.aggregate.finances.latestSpending:
            if i.sum:
                scale = get_scaling_factor(i.sum)
                i.sumIncomeText = "£" + scale[2].format(i.sum / scale[0])
            i.name = new_bucket_labels.get(i.name or i.key, i.name or i.key)

    def get_charity(self):
        if self.list_:
            return self.list_[0]

    def set_charts(self, selected_countries: Optional[list[Country]] = None):
        self.charts = self.get_charts(selected_countries)

    def get_charts(self, selected_countries: Optional[list[Country]] = None):
        if not self.aggregate:
            return None

        for i in CLASSIFICATION.keys():
            for x in getattr(self.aggregate, i):
                x.name = CLASSIFICATION.get(i, {}).get(x.key, x.key)

        if selected_countries and len(selected_countries) == 1:
            selected_country = selected_countries[0]
            countries = [
                c for c in self.aggregate.areas if c.key != selected_country.id
            ]
        else:
            countries = self.aggregate.areas

        for country in countries:
            country_record = get_country_by_id(country.key)
            if not country_record:
                warn(f"Country with ID {country.key} not found.")
                continue
            country.name = country_record.name if country.key else ""

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

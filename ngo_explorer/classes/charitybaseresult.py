import copy

from ..utils.countries import get_country_by_id
from ..utils.utils import get_scaling_factor
from ..utils.charts import line_chart, horizontal_bar, word_cloud
from ..utils.filters import CLASSIFICATION
from .charitybasecharity import CharityBaseCharity

class CharityBaseResult(object):

    def __init__(self, result):
        result = result.get("data", {}).get("CHC", {}).get("getCharities")
        self.aggregate = result.get("aggregate")
        self.count = result.get("count")
        self.list = [CharityBaseCharity(c) for c in result.get("list", [])]

        self._parse_aggregates()
        self._parse_income_buckets()

    def _parse_aggregates(self):
        if not self.aggregate:
            return

        for k in self.aggregate.keys():
            if "buckets" in self.aggregate[k]:
                self.aggregate[k] = self.aggregate[k]["buckets"]
            elif isinstance(self.aggregate[k], dict):
                for j in self.aggregate[k].keys():
                    if "buckets" in self.aggregate[k][j]:
                        self.aggregate[k][j] = self.aggregate[k][j]["buckets"]

        if self.aggregate.get("finances", {}).get("latestIncome", {}):
            self.total_income = sum([
                f["sumIncome"]
                for f in self.aggregate.get("finances", {}).get("latestIncome", {})
            ])

    def _parse_income_buckets(self):

        if not self.aggregate:
            return
        income_buckets = self.aggregate.get("finances", {}).get("latestIncome", {})
        if not income_buckets:
            return

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
            id_ = new_bucket_labels.get(i["name"], i["key"])
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
            i["sumIncomeText"] = "£" + \
                scale[2].format(i["sumIncome"] / scale[0])
            income_buckets.append(i)

        self.aggregate["finances"]["latestIncome"] = income_buckets

    def get_charity(self):
        if len(self.list):
            return self.list[0]

    def set_charts(self, selected_countries=None):
        self.charts = self.get_charts(selected_countries)

    def get_charts(self, selected_countries=None):

        if not self.aggregate:
            return None

        for i in CLASSIFICATION.keys():
            for x in self.aggregate[i]:
                x['name'] = CLASSIFICATION.get(i, {}).get(x["key"], x["key"])

        countries = [
            {"count": i["count"], **
                get_country_by_id(i['key']), "id": i["key"]}
            for i in self.aggregate["areas"]
            if get_country_by_id(i['key'])
        ]
        if selected_countries and len(selected_countries) == 1:
            selected_country = selected_countries[0]['id']
            countries = [c for c in countries if c['id'] != selected_country]

        return {
            "count": horizontal_bar(self.aggregate["finances"]["latestIncome"], "count"),
            "amount": horizontal_bar(self.aggregate["finances"]["latestIncome"], "sumIncome", "sumIncomeText", log_axis=True),
            "countries": horizontal_bar(countries[0:12], "count"),
            **{
                k: horizontal_bar(self.aggregate[k], "count")
                for k in CLASSIFICATION.keys()
            },
            "word_cloud": word_cloud(self.list),
        }

import json
import os
import copy
from datetime import datetime

from flask import current_app
from graphqlclient import GraphQLClient
import requests

from .filters import CLASSIFICATION
from .countries import get_country_by_id
from .utils import get_scaling_factor

GQL_QUERIES = {}
for f in os.scandir(os.path.join(os.path.dirname(__file__), 'queries')):
    if f.name.endswith(".gql"):
        with open(f.path) as a:
            GQL_QUERIES[f.name.replace(".gql", "")] = a.read()

class GraphQLClientRequests(GraphQLClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        if self.token is not None:
            headers[self.headername] = '{}'.format(self.token)

        r = requests.post(self.endpoint, json=data, headers=headers)
        r.raise_for_status()
        return r.json()


def fetch_charitybase(countries:list = None, ids:list = None, filters=None, limit: int = 10, skip: int = 0, query: str = "charity_aggregation", query_fields: dict = None):
    client = GraphQLClientRequests('https://charitybase.uk/api/graphql')
    client.inject_token('Apikey {}'.format(current_app.config["CHARITYBASE_API_KEY"]))

    variables = {
        "filters": {
        },
        "limit": limit,
        "skip": skip,
    }

    if countries:
        variables["filters"]["areas"] = {
            "some": [c['id'] for c in countries],
            "length": {
                "lte": filters.get("max_countries", 50)
            }
        }
    
    if ids:
        variables["filters"]["id"] = ids

    if filters:
        if "search" in filters:
            variables["filters"]["search"] = filters["search"]

        for c in CLASSIFICATION.keys():
            if c in filters:
                variables["filters"][c] = {
                    "some": filters[c]
                }

        if "max_income" or "min_income" in filters:
            variables["filters"]["finances"] = {
                "latestIncome": {}
            }
            if "max_income" in filters:
                variables["filters"]["finances"]["latestIncome"]["lte"] = filters["max_income"]
            if "min_income" in filters:
                variables["filters"]["finances"]["latestIncome"]["gte"] = filters["min_income"]

        if "countries" in filters:
            countries = [c for c in variables["filters"]["areas"]["some"] if c in filters["countries"]]
            if countries:
                variables["filters"]["areas"]["some"] = countries

        if filters.get("regions"):
            if "geo" not in variables["filters"]:
                variables["filters"]["geo"] = {}
            if countries:
                variables["filters"]["geo"]["region"] = filters.get("regions")

        if filters.get("exclude_grantmakers"):
            if "operations" not in variables["filters"]:
                variables["filters"]["operations"] = {}
            variables["filters"]["operations"]["notSome"] = ["302"]

        if filters.get("exclude_religious"):
            if "causes" not in variables["filters"]:
                variables["filters"]["causes"] = {}
            variables["filters"]["causes"]["notSome"] = ["108"]
    
    if query == "charity_download":
        query_str = GQL_QUERIES[query] % dict_to_gql(query_fields, 8)
    else:
        query_str = GQL_QUERIES[query]

    result = client.execute(query_str, variables)
    
    if result.get("errors") or not result.get("data", {}).get("CHC", {}).get("getCharities"):
        raise Exception(result.get("errors"))
    return CharityBaseResult(result)


def dict_to_gql(values, indent=0):
        lines = []
        for k, v in values.items():
            if isinstance(v, dict) and v:
                lines.append((" " * indent) + k + "{")
                lines.append(dict_to_gql(v, indent+2))
                lines.append((" " * indent) + "}")
            else:
                lines.append((" " * indent) + k)
        return "\n".join(lines)


with open(os.path.join(os.path.dirname(__file__), 'iati', "oipa-country-participant-gb.json")) as iati_file:
    IATI_DATA = json.load(iati_file)

def fetch_iati(countries: list):
    country_codes = [c["iso2"] for c in countries]
    return {
        k: v for k, v in IATI_DATA.items() if k in country_codes
    }


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

    def _parse_income_buckets(self):

        if not self.aggregate:
            return
        income_buckets = self.aggregate.get("income")
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
            i["sumIncomeText"] = "£" + scale[2].format(i["sumIncome"] / scale[0])
            income_buckets.append(i)

        self.aggregate["income"] = income_buckets

    def get_charity(self):
        if len(self.list):
            return self.list[0]


class CharityBaseCharity(object):

    date_format = "%Y-%m-%d"

    def __init__(self, chardata):
        for k, v in chardata.items():
            setattr(self, k, v)

        self._set_name()
        self._get_countries()
        self._parse_website()
        self._parse_finances()

    def _set_name(self):
        for n in self.names:
            if n["primary"]:
                self.name = n["value"]

    def _get_countries(self):
        areas = []
        countries = []
        if hasattr(self, "areas"):
            for a in self.areas:
                c = get_country_by_id(a["id"])
                if c:
                    countries.append(c)
                else:
                    areas.append(a)
        self.areas = areas
        self.countries = countries

    def _parse_website(self):
        if getattr(self, "website"):
            self.website = self.website.strip()
            if not self.website.startswith("http"):
                self.website = "//" + self.website

    def _parse_finances(self):
        if getattr(self, "finances"):
            for f in self.finances:
                if f.get("financialYear", {}).get("end"):
                    f["financialYear"]["end"] = datetime.strptime(
                        f["financialYear"]["end"][0:10], self.date_format)
                if f.get("financialYear", {}).get("start"):
                    f["financialYear"]["start"] = datetime.strptime(
                        f["financialYear"]["start"][0:10], self.date_format)

    # def flat_dict(self):


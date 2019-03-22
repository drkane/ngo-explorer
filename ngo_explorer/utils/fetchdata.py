import json
import os
import copy
from datetime import datetime

from flask import current_app

from .filters import CLASSIFICATION
from ..classes import GraphQLClientRequests, CharityBaseResult, CharityBaseCharity
from .countries import get_country_by_id

GQL_QUERIES = {}
for f in os.scandir(os.path.join(os.path.dirname(__file__), 'queries')):
    if f.name.endswith(".gql"):
        with open(f.path) as a:
            GQL_QUERIES[f.name.replace(".gql", "")] = a.read()


def fetch_charitybase(
    countries:list = None,
    ids:list = None,
    filters:dict = None,
    limit:int = 10,
    skip:int = 0,
    query:str = "charity_aggregation",
    query_fields:dict = None,
    all_finances: bool = False,
    sort: str = "default",
    ):
    client = GraphQLClientRequests('https://charitybase.uk/api/graphql')
    client.inject_token('Apikey {}'.format(current_app.config["CHARITYBASE_API_KEY"]))

    variables = {
        "filters": {
        },
        "limit": limit,
        "skip": skip,
        "sort": sort,
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

    if all_finances:
        variables["allFinances"] = True

    if filters:
        if "search" in filters:
            variables["filters"]["search"] = filters["search"]

        for c in CLASSIFICATION.keys():
            if c in filters:
                variables["filters"][c] = {
                    "some": filters[c]
                }

        if "max_income" in filters or "min_income" in filters:
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
            region = filters.get("regions")
            if region.startswith("E"):
                variables["filters"]["geo"]["region"] = region
            else:
                variables["filters"]["geo"]["country"] = region

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
    
    if result.get("errors") and not result.get("data", {}).get("CHC", {}).get("getCharities"):
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

def fetch_iati_by_charity(orgids):
    if not orgids:
        return []
    iati_activity = []
    for country_code, iati_orgs in IATI_DATA.items():
        for org in iati_orgs:
            if org["ref"] in orgids:
                org["country"] = get_country_by_id(country_code)
                if org["country"]:
                    iati_activity.append(org)
    return iati_activity

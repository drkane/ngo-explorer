import json
import os

from flask import current_app
from graphqlclient import GraphQLClient
import requests

from .filters import CLASSIFICATION

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


def fetch_charitybase(countries: list, filters=None, limit:int=10, skip: int=0, query: str="charity_aggregation"):
    client = GraphQLClientRequests('https://charitybase.uk/api/graphql')
    client.inject_token('Apikey {}'.format(current_app.config["CHARITYBASE_API_KEY"]))

    variables = {
        "filters": {
            "areas": {
                "some": [c['id'] for c in countries],
                "length": {
                    "lessThanInclusive": filters.get("max_countries", 50)
                }
            }
        },
        "limit": limit
    }

    if filters:
        if "search" in filters:
            variables["filters"]["search"] = filters["search"]

        for c in CLASSIFICATION.keys():
            if c in filters:
                variables["filters"][c] = {
                    "some": filters[c]
                }
    
    if query=="charity_list" and skip > 0:
        variables["skip"] = skip

    result = client.execute(GQL_QUERIES[query], variables)
    
    if result.get("errors") or not result.get("data", {}).get("CHC", {}).get("getCharities"):
        raise Exception(result.get("errors"))
    return result.get("data", {}).get("CHC", {}).get("getCharities")

def fetch_charitybase_fromids(ids: list):
    client = GraphQLClientRequests('https://charitybase.uk/api/graphql')
    client.inject_token('Apikey {}'.format(current_app.config["CHARITYBASE_API_KEY"]))

    result = client.execute(GQL_QUERIES["charity_aggregation"], {
        "filters": {
            "id": ids
        }
    })
    
    if result.get("errors") or not result.get("data", {}).get("CHC", {}).get("getCharities"):
        raise Exception(result.get("errors"))
    return result.get("data", {}).get("CHC", {}).get("getCharities")


with open(os.path.join(os.path.dirname(__file__), 'iati', "oipa-country-participant-gb.json")) as iati_file:
    IATI_DATA = json.load(iati_file)

def fetch_iati(countries: list):
    country_codes = [c["iso2"] for c in countries]
    return {
        k: v for k, v in IATI_DATA.items() if k in country_codes
    }

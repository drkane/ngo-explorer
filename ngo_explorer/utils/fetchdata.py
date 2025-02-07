import json
import os
from typing import Literal

import psycopg
from flask import current_app
from sqlite_utils import Database

from ngo_explorer.classes import CharityLookupResult, GraphQLClientRequests
from ngo_explorer.utils.countries import get_country_by_id
from ngo_explorer.utils.filters import CLASSIFICATION

QueryType = Literal[
    "all_charities", "charity_aggregation", "charity_download", "charity_list"
]

GQL_QUERIES: dict[QueryType, str] = {}
for f in os.scandir(os.path.join(os.path.dirname(__file__), "queries")):
    if f.name.endswith(".gql"):
        with open(f.path) as a:
            GQL_QUERIES[f.name.replace(".gql", "")] = a.read()


FTC_QUERIES = {
    "all_charities": """
        SELECT CASE WHEN c.spending >= 1000000000 THEN 9 
            WHEN c.spending >= 316227766 THEN 8.5
            WHEN c.spending >= 100000000 THEN 8
            WHEN c.spending >= 31622777 THEN 7.5
            WHEN c.spending >= 10000000 THEN 7
            WHEN c.spending >= 3162278 THEN 6.5
            WHEN c.spending >= 1000000 THEN 6
            WHEN c.spending >= 316228 THEN 5.5
            WHEN c.spending >= 100000 THEN 5
            WHEN c.spending >= 31623 THEN 4.5
            WHEN c.spending >= 10000 THEN 4
            WHEN c.spending >= 3162 THEN 3.5
            WHEN c.spending >= 1000 THEN 3
            WHEN c.spending >= 316 THEN 2.5
            WHEN c.spending >= 100 THEN 2
            WHEN c.spending >= 32 THEN 1.5
            WHEN c.spending >= 10 THEN 1
            WHEN c.spending >= 3 THEN 0.5
            WHEN c.spending >= 1 THEN 0
            ELSE NULL END AS key,
            CASE WHEN c.spending >= 1000000000 THEN 'Min. £1000000000'
                WHEN c.spending >= 316227766 THEN 'Min. £316227766'
                WHEN c.spending >= 100000000 THEN 'Min. £100000000'
                WHEN c.spending >= 31622777 THEN 'Min. £31622777'
                WHEN c.spending >= 10000000 THEN 'Min. £10000000'
                WHEN c.spending >= 3162278 THEN 'Min. £3162278'
                WHEN c.spending >= 1000000 THEN 'Min. £1000000'
                WHEN c.spending >= 316228 THEN 'Min. £316228'
                WHEN c.spending >= 100000 THEN 'Min. £100000'
                WHEN c.spending >= 31623 THEN 'Min. £31623'
                WHEN c.spending >= 10000 THEN 'Min. £10000'
                WHEN c.spending >= 3162 THEN 'Min. £3162'
                WHEN c.spending >= 1000 THEN 'Min. £1000'
                WHEN c.spending >= 316 THEN 'Min. £316'
                WHEN c.spending >= 100 THEN 'Min. £100'
                WHEN c.spending >= 32 THEN 'Min. £32'
                WHEN c.spending >= 10 THEN 'Min. £10'
                WHEN c.spending >= 3 THEN 'Min. £3'
                WHEN c.spending >= 1 THEN 'Min. £1'
                ELSE NULL END AS name,
            count(*) AS count,
            sum(c.spending) AS sum
        FROM charity_charity c
        WHERE c.active 
            AND c."source" = 'ccew'
        GROUP BY 1, 2
        ORDER BY 1 ASC
        """,
    "charity_list": """
        WITH classification AS (
            SELECT 'GB-CHC-' || cc.registered_charity_number AS charity_id,
                jsonb_agg(
                    jsonb_build_object('id', cc.classification_code )
                ) FILTER (WHERE classification_type = 'How') AS operations,
                jsonb_agg(
                    jsonb_build_object('id', cc.classification_code )
                ) FILTER (WHERE classification_type = 'What') AS causes,
                jsonb_agg(
                    jsonb_build_object('id', cc.classification_code )
                ) FILTER (WHERE classification_type = 'Who') AS beneficiaries
            FROM charity_ccewcharityclassification cc 
            GROUP BY 1
        ),
        "location" AS (
            SELECT org_id,
                jsonb_build_object(
                    'latitude', l.geo_lat,
                    'longitude', l.geo_long,
                    'region', rgn."name",
                    'country', ctry."name"
                ) AS geo
            FROM ftc_organisationlocation l
                LEFT OUTER JOIN geo_geolookup ctry
                    ON l.geo_ctry = ctry."geoCode" 
                LEFT OUTER JOIN geo_geolookup rgn
                    ON l.geo_rgn = rgn."geoCode" 
            WHERE l."locationType" = 'HQ'
        ),
        "areas" AS (
            SELECT charity_id,
                jsonb_agg(
                    jsonb_build_object(
                        'name', aoo.aooname,
                        'id', aoo.aootype || '-' || aoo.aookey
                    )
                ) AS areas
            FROM charity_charity_areas_of_operation caoo
                INNER JOIN charity_areaofoperation aoo
                    ON caoo.areaofoperation_id = aoo.id
            GROUP BY 1
        )
        SELECT replace(id, 'GB-CHC-', '') AS id,
            jsonb_build_array(
                jsonb_build_object('value', name, 'primary', true)
            ) AS names,
            c.activities AS activities,
            COALESCE(areas.areas, jsonb_build_array()) AS areas,
            jsonb_build_array(
                jsonb_build_object(
                    'income', c.income,
                    'spending', c.spending,
                    'financialYear', jsonb_build_object(
                        'end', c.latest_fye
                    )
                )
            ) AS finances,
            CASE WHEN c.company_number IS NOT NULL 
                THEN jsonb_build_array(jsonb_build_object('id', id), jsonb_build_object('id', 'GB-COH-' || c.company_number)) 
                ELSE jsonb_build_array(jsonb_build_object('id', id))  
                END AS orgIds,
            COALESCE(classification.operations, jsonb_build_array())  AS operations,
            "location".geo AS geo,
            jsonb_build_array(
                jsonb_build_object(
                    'registrationDate', c.date_registered,
                    'removalDate', c.date_removed
                )
            ) AS registrations,
            c.web AS website
        FROM charity_charity c
            LEFT OUTER JOIN classification
                ON c.id = classification.charity_id 
            LEFT OUTER JOIN "location"
                ON c.id = "location".org_id 
            LEFT OUTER JOIN "areas"
                ON c.id = "areas".charity_id
        """,
}

SORT_OPTIONS = {
    "age_asc": "json_extract(registrations, '$[0].registrationDate') ASC",
    "age_desc": "json_extract(registrations, '$[0].registrationDate') DESC",
    "default": "json_extract(finances, '$[0].spending') DESC",
    "income_asc": "json_extract(finances, '$[0].income') ASC",
    "income_desc": "json_extract(finances, '$[0].income') DESC",
    "random": " DESC",
    "spending_asc": "json_extract(finances, '$[0].spending') ASC",
    "spending_desc": "json_extract(finances, '$[0].spending') DESC",
}


def fetch_findthatcharity(
    countries: list = None,
    ids: list = None,
    filters: dict = None,
    limit: int = 10,
    skip: int = 0,
    query: QueryType = "charity_aggregation",
    query_fields: dict = None,
    all_finances: bool = False,
    sort: str = "default",
) -> CharityLookupResult:
    if query == "all_charities":
        with psycopg.connect(current_app.config["FTC_DB_URL"]) as conn:
            with conn.cursor() as cur:
                cur.execute(FTC_QUERIES["all_charities"])
                buckets = []
                total_count = 0
                for record in cur.fetchall():
                    total_count += record[2]
                    if record[0] is None:
                        continue
                    buckets.append(
                        {
                            "key": int(record[0]) if record[0] is not None else None,
                            "name": record[1],
                            "count": int(record[2]) if record[2] is not None else None,
                            "sum": int(record[3]) if record[3] is not None else None,
                        }
                    )
                return CharityLookupResult(
                    {
                        "data": {
                            "CHC": {
                                "getCharities": {
                                    "aggregate": {
                                        "finances": {
                                            "latestSpending": {"buckets": buckets}
                                        }
                                    },
                                    "count": total_count,
                                }
                            }
                        }
                    }
                )
    db = Database(current_app.config["DB_LOCATION"])
    where_conditions = ["1=1"]
    where_args = {}

    if countries:
        for i, c in enumerate(countries):
            country_arg = "country{}".format(i)
            or_conditions = []
            or_conditions.append(
                f"EXISTS (SELECT 1 FROM json_each(countries) WHERE value = :{country_arg})"
            )
            where_args[country_arg] = c["id"]
        where_conditions.append("(" + " OR ".join(or_conditions) + ")")

        where_conditions.append("json_array_length(countries) <= :max_countries")
        where_args["max_countries"] = filters.get("max_countries", 50)

    if ids:
        where_conditions.append("id IN :ids")
        where_args["ids"] = tuple(ids)

    where_str = " AND ".join(where_conditions)

    print(where_str)
    if query == "charity_list":
        charities = []
        for record in db["charity"].rows_where(
            where=where_str,
            where_args=where_args,
            limit=limit,
            offset=skip,
            order_by=SORT_OPTIONS.get(sort, SORT_OPTIONS["default"]),
        ):
            if all_finances:
                charity_finances = record["all_finances"]
            else:
                charity_finances = record["finances"]
            charities.append(
                {
                    "id": record["id"],
                    "names": json.loads(record["names"]) if record["names"] else [],
                    "activities": record["activities"],
                    "areas": json.loads(record["areas"]) if record["areas"] else [],
                    "finances": (
                        json.loads(charity_finances) if charity_finances else []
                    ),
                    "orgIds": json.loads(record["orgids"]) if record["orgids"] else [],
                    "operations": (
                        json.loads(record["operations"]) if record["operations"] else []
                    ),
                    "geo": json.loads(record["geo"]) if record["geo"] else {},
                    "registrations": (
                        json.loads(record["registrations"])
                        if record["registrations"]
                        else []
                    ),
                    "website": record["website"],
                }
            )
        return CharityLookupResult(
            {
                "data": {
                    "CHC": {
                        "getCharities": {
                            "list": charities,
                            "count": db["charity"].count_where(
                                where=where_str, where_args=where_args
                            ),
                        }
                    }
                }
            }
        )


def fetch_charitybase(
    countries: list = None,
    ids: list = None,
    filters: dict = None,
    limit: int = 10,
    skip: int = 0,
    query: QueryType = "charity_aggregation",
    query_fields: dict = None,
    all_finances: bool = False,
    sort: str = "default",
) -> CharityLookupResult:
    print(query)
    if query in ("all_charities", "charity_list"):
        return fetch_findthatcharity(
            countries,
            ids,
            filters,
            limit,
            skip,
            query,
            query_fields,
            all_finances,
            sort,
        )
    client = GraphQLClientRequests(current_app.config["CHARITYBASE_URL"])
    client.inject_token("Apikey {}".format(current_app.config["CHARITYBASE_API_KEY"]))

    variables = {
        "filters": {},
        "limit": limit,
        "skip": skip,
        "sort": sort,
    }

    if countries:
        variables["filters"]["areas"] = {
            "some": [c["id"] for c in countries],
            "length": {"lte": filters.get("max_countries", 50)},
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
                variables["filters"][c] = {"some": filters[c]}

        if "max_income" in filters or "min_income" in filters:
            variables["filters"]["finances"] = {"latestIncome": {}}
            if "max_income" in filters:
                variables["filters"]["finances"]["latestIncome"]["lte"] = filters[
                    "max_income"
                ]
            if "min_income" in filters:
                variables["filters"]["finances"]["latestIncome"]["gte"] = filters[
                    "min_income"
                ]

        if "countries" in filters:
            countries = [
                c
                for c in variables["filters"]["areas"]["some"]
                if c in filters["countries"]
            ]
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

    if result.get("errors"):
        for e in result.get("errors", []):
            current_app.logger.warning(e)
    return CharityLookupResult(result)


def dict_to_gql(values, indent=0):
    lines = []
    for k, v in values.items():
        if isinstance(v, dict) and v:
            lines.append((" " * indent) + k + "{")
            lines.append(dict_to_gql(v, indent + 2))
            lines.append((" " * indent) + "}")
        else:
            lines.append((" " * indent) + k)
    return "\n".join(lines)


with open(
    os.path.join(os.path.dirname(__file__), "iati", "oipa-country-participant-gb.json")
) as iati_file:
    IATI_DATA = json.load(iati_file)


def fetch_iati(countries: list):
    country_codes = [c["iso2"] for c in countries]
    return {k: v for k, v in IATI_DATA.items() if k in country_codes}


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

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

from sqlite_utils import Database

from ngo_explorer.classes.charity import Charity
from ngo_explorer.classes.countries import Country
from ngo_explorer.classes.iati import OipaItem, OipaItemOrg
from ngo_explorer.classes.result import Result
from ngo_explorer.classes.results import (
    ResultAggregate,
    ResultBucket,
)
from ngo_explorer.db import get_db
from ngo_explorer.utils.countries import get_country_by_id
from ngo_explorer.utils.filters import CLASSIFICATION, Filters

QueryType = Literal["charity_aggregation", "charity_download", "charity_list"]

AGGREGATE_SQL = {
    "latestSpending": """
        SELECT CASE WHEN json_extract(finances, '$[0].spending') >= 10000000 THEN 5
            WHEN json_extract(finances, '$[0].spending') >= 1000000 THEN 4
            WHEN json_extract(finances, '$[0].spending') >= 100000 THEN 3
            WHEN json_extract(finances, '$[0].spending') >= 10000 THEN 2
            WHEN json_extract(finances, '$[0].spending') >= 0 THEN 1
            ELSE NULL END AS key,
            CASE WHEN json_extract(finances, '$[0].spending') >= 10000000 THEN 'Over £10m'
            WHEN json_extract(finances, '$[0].spending') >= 1000000 THEN '£1m-£10m'
            WHEN json_extract(finances, '$[0].spending') >= 100000 THEN '£100k-£1m'
            WHEN json_extract(finances, '$[0].spending') >= 10000 THEN '£10k-£100k'
            WHEN json_extract(finances, '$[0].spending') >= 0 THEN 'Under £10k'
                ELSE NULL END AS name,
            count(*) AS count,
            sum(json_extract(finances, '$[0].spending')) AS sum
        FROM charity
        WHERE {where_str}
        GROUP BY 1, 2
        ORDER BY 1 ASC
        """,
    "causes": """
            SELECT json_extract(json_each.value, '$.id') AS "key",
                json_extract(json_each.value, '$.id') AS "name",
                count(*) as "count",
                null as "sum"
            FROM charity, json_each(charity.{op_type})
            WHERE {where_str}
            GROUP BY 1
            ORDER BY 3 DESC
            """,
    "countries": """
            SELECT json_each.value AS "key",
                json_each.value AS "name",
                count(*) as "count",
                null as "sum"
            FROM charity, json_each(charity.countries)
            WHERE {where_str}
            GROUP BY 1
            ORDER BY 3 DESC
            """,
    "region": """
            SELECT json_extract(geo, '$.region_code') AS "key",
                json_extract(geo, '$.region_name') AS "name",
                count(*) as "count",
                null as "sum"
            FROM charity
            WHERE {where_str}
            GROUP BY 1
            ORDER BY 3 DESC
            """,
    "uk_country": """
            SELECT json_extract(geo, '$.country_code') AS "key",
                json_extract(geo, '$.country_name') AS "name",
                count(*) as "count",
                null as "sum"
            FROM charity
            WHERE {where_str}
            GROUP BY 1
            ORDER BY 3 DESC
            """,
}


SORT_OPTIONS = {
    "age_asc": "json_extract(registrations, '$[0].registrationDate') ASC",
    "age_desc": "json_extract(registrations, '$[0].registrationDate') DESC",
    "default": "json_extract(finances, '$[0].spending') DESC",
    "income_asc": "json_extract(finances, '$[0].income') ASC",
    "income_desc": "json_extract(finances, '$[0].income') DESC",
    "random": "RANDOM() DESC",
    "spending_asc": "json_extract(finances, '$[0].spending') ASC",
    "spending_desc": "json_extract(finances, '$[0].spending') DESC",
}


@dataclass
class AllCharitiesResult:
    total_income: int
    total_charities: int
    last_updated: datetime


def fetch_all_charities() -> Optional[AllCharitiesResult]:
    db: Database = get_db()
    for row in db["stats"].rows:
        return AllCharitiesResult(
            total_income=row["total_income"],
            total_charities=row["total_charities"],
            last_updated=datetime.fromisoformat(row["last_updated"]),
        )


def fetch_charity_details(
    countries: Optional[list[Country]] = None,
    ids: Optional[list[str]] = None,
    filters: Optional[Filters] = None,
    limit: int = 10,
    skip: int = 0,
    query: QueryType = "charity_aggregation",
    query_fields: Optional[dict] = None,
    all_finances: bool = False,
    sort: str = "default",
) -> Result:
    db: Database = get_db()
    where_conditions: list[str] = ["1=1"]
    where_args = {}

    if countries:
        or_conditions = []
        for i, country in enumerate(countries):
            country_arg = f"country{i}"
            or_conditions.append(f"value = :{country_arg}")
            where_args[country_arg] = country.iso2
        where_conditions.append(
            "EXISTS (SELECT 1 FROM json_each(countries) WHERE "
            + " OR ".join(or_conditions)
            + ")"
        )

        where_conditions.append("json_array_length(countries) <= :max_countries")
        where_args["max_countries"] = getattr(filters, "max_countries", 50)

    if ids:
        or_conditions = []
        for i, id_ in enumerate(ids):
            id_arg = f"id{i}"
            or_conditions.append(f"[charity].[id] = :{id_arg}")
            where_args[id_arg] = id_
        where_conditions.append("(" + " OR ".join(or_conditions) + ")")

    if filters:
        if filters.search:
            where_conditions.append(
                "charity.id IN (SELECT charity_fts.id FROM charity_fts(:search))"
            )
            where_args["search"] = filters.search

        for c in CLASSIFICATION.keys():
            if getattr(filters, c, None):
                or_conditions = []
                for i, value in enumerate(getattr(filters, c, [])):
                    value_arg = f"{c}{i}"
                    or_conditions.append(
                        f"json_extract(json_each.value, '$.id') = :{value_arg}"
                    )
                    where_args[value_arg] = int(value)
                where_conditions.append(
                    f"EXISTS (SELECT 1 FROM json_each({c}) WHERE "
                    + " OR ".join(or_conditions)
                    + ")"
                )

        if filters.max_income:
            where_conditions.append(
                "json_extract(finances, '$[0].income') <= :max_income"
            )
            where_args["max_income"] = filters.max_income
        if filters.min_income:
            where_conditions.append(
                "json_extract(finances, '$[0].income') >= :min_income"
            )
            where_args["min_income"] = filters.min_income

        if filters.countries:
            or_conditions = []
            for i, country in enumerate(filters.countries):
                country_arg = "countryb{}".format(i)
                or_conditions.append(f"value = :{country_arg}")
                where_args[country_arg] = country
            where_conditions.append(
                "EXISTS (SELECT 1 FROM json_each(countries) WHERE "
                + " OR ".join(or_conditions)
                + ")"
            )

        if filters.regions:
            if filters.regions.startswith("E"):
                where_conditions.append("json_extract(geo, '$.codes.region') = :region")
            else:
                where_conditions.append(
                    "json_extract(geo, '$.codes.country') = :region"
                )
            where_args["region"] = filters.regions

        if filters.exclude_grantmakers:
            where_conditions.append(
                "NOT EXISTS (SELECT 1 FROM json_each(operations) WHERE json_extract(json_each.value, '$.id') = :exclude_grantmakers)"
            )
            where_args["exclude_grantmakers"] = 302

        if filters.exclude_religious:
            where_conditions.append(
                "NOT EXISTS (SELECT 1 FROM json_each(causes) WHERE json_extract(json_each.value, '$.id') = :exclude_religious)"
            )
            where_args["exclude_religious"] = 108

    where_str = " AND ".join(where_conditions)
    inflation: dict[str, float] = {
        row["year"]: float(row["value"]) for row in db["inflation"].rows
    }

    charities = [
        Charity.from_db(record, all_finances, inflation)
        for record in db["charity"].rows_where(
            where=where_str,
            where_args=where_args,
            limit=limit,
            offset=skip,
            order_by=SORT_OPTIONS.get(sort, SORT_OPTIONS["default"]),
        )
    ]

    result = Result(
        count=db["charity"].count_where(where=where_str, where_args=where_args),
        list_=charities,
        aggregate=None,
    )

    if query == "charity_aggregation":
        result.aggregate = ResultAggregate()

        result.aggregate.finances.latestSpending = [
            ResultBucket(**row)
            for row in db.query(
                AGGREGATE_SQL["latestSpending"].format(where_str=where_str), where_args
            )
        ]
        for op_type in ["causes", "beneficiaries", "operations"]:
            setattr(result.aggregate, op_type, [])
            for row in db.query(
                AGGREGATE_SQL["causes"].format(where_str=where_str, op_type=op_type),
                where_args,
            ):
                row["key"] = str(row["key"])
                row["name"] = CLASSIFICATION[op_type][row["key"]]
                getattr(result.aggregate, op_type, []).append(ResultBucket(**row))
        result.aggregate.areas = [
            ResultBucket(**row)
            for row in db.query(
                AGGREGATE_SQL["countries"].format(where_str=where_str), where_args
            )
        ]
        result.aggregate.geo.region = [
            ResultBucket(**row)
            for row in db.query(
                AGGREGATE_SQL["region"].format(where_str=where_str), where_args
            )
        ]
        result.aggregate.geo.country = [
            ResultBucket(**row)
            for row in db.query(
                AGGREGATE_SQL["uk_country"].format(where_str=where_str), where_args
            )
        ]

        result._parse_aggregates()
        result._parse_income_buckets()

    return result


with open(
    os.path.join(os.path.dirname(__file__), "iati", "oipa-country-participant-gb.json")
) as iati_file:
    IATI_DATA: dict[str, list[OipaItem]] = json.load(iati_file)


def fetch_iati(countries: list[Country]) -> dict[str, list[OipaItem]]:
    country_codes = [country.iso2 for country in countries]
    return {k: v for k, v in IATI_DATA.items() if k in country_codes}


def fetch_iati_by_charity(orgids: list[str]) -> list[OipaItemOrg]:
    iati_activity: list[OipaItemOrg] = []
    if not orgids:
        return iati_activity
    for country_code, iati_orgs in IATI_DATA.items():
        for org in iati_orgs:
            if org["ref"] in orgids:
                org_item = OipaItemOrg(
                    ref=org["ref"],
                    name=org["name"],
                    count=org["count"],
                    country=get_country_by_id(country_code),
                )
                if org_item.country:
                    iati_activity.append(org_item)
    return iati_activity

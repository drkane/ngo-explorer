import json
import os
from dataclasses import dataclass
from typing import Literal, Optional, TypedDict

from flask import current_app
from sqlite_utils import Database

from ngo_explorer.classes import CharityLookupCharity, CharityLookupResult
from ngo_explorer.classes.charitylookupresult import (
    ResultAggregate,
    ResultBucket,
)
from ngo_explorer.utils.countries import Country, get_country_by_id
from ngo_explorer.utils.filters import CLASSIFICATION, Filters

QueryType = Literal["charity_aggregation", "charity_download", "charity_list"]

AGGREGATE_SQL = {
    "latestSpending": """
        SELECT CASE WHEN json_extract(finances, '$[0].spending') >= 1000000000 THEN 9 
            WHEN json_extract(finances, '$[0].spending') >= 316227766 THEN 8.5
            WHEN json_extract(finances, '$[0].spending') >= 100000000 THEN 8
            WHEN json_extract(finances, '$[0].spending') >= 31622777 THEN 7.5
            WHEN json_extract(finances, '$[0].spending') >= 10000000 THEN 7
            WHEN json_extract(finances, '$[0].spending') >= 3162278 THEN 6.5
            WHEN json_extract(finances, '$[0].spending') >= 1000000 THEN 6
            WHEN json_extract(finances, '$[0].spending') >= 316228 THEN 5.5
            WHEN json_extract(finances, '$[0].spending') >= 100000 THEN 5
            WHEN json_extract(finances, '$[0].spending') >= 31623 THEN 4.5
            WHEN json_extract(finances, '$[0].spending') >= 10000 THEN 4
            WHEN json_extract(finances, '$[0].spending') >= 3162 THEN 3.5
            WHEN json_extract(finances, '$[0].spending') >= 1000 THEN 3
            WHEN json_extract(finances, '$[0].spending') >= 316 THEN 2.5
            WHEN json_extract(finances, '$[0].spending') >= 100 THEN 2
            WHEN json_extract(finances, '$[0].spending') >= 32 THEN 1.5
            WHEN json_extract(finances, '$[0].spending') >= 10 THEN 1
            WHEN json_extract(finances, '$[0].spending') >= 3 THEN 0.5
            WHEN json_extract(finances, '$[0].spending') >= 1 THEN 0
            ELSE NULL END AS key,
            CASE WHEN json_extract(finances, '$[0].spending') >= 1000000000 THEN 'Min. £1000000000'
                WHEN json_extract(finances, '$[0].spending') >= 316227766 THEN 'Min. £316227766'
                WHEN json_extract(finances, '$[0].spending') >= 100000000 THEN 'Min. £100000000'
                WHEN json_extract(finances, '$[0].spending') >= 31622777 THEN 'Min. £31622777'
                WHEN json_extract(finances, '$[0].spending') >= 10000000 THEN 'Min. £10000000'
                WHEN json_extract(finances, '$[0].spending') >= 3162278 THEN 'Min. £3162278'
                WHEN json_extract(finances, '$[0].spending') >= 1000000 THEN 'Min. £1000000'
                WHEN json_extract(finances, '$[0].spending') >= 316228 THEN 'Min. £316228'
                WHEN json_extract(finances, '$[0].spending') >= 100000 THEN 'Min. £100000'
                WHEN json_extract(finances, '$[0].spending') >= 31623 THEN 'Min. £31623'
                WHEN json_extract(finances, '$[0].spending') >= 10000 THEN 'Min. £10000'
                WHEN json_extract(finances, '$[0].spending') >= 3162 THEN 'Min. £3162'
                WHEN json_extract(finances, '$[0].spending') >= 1000 THEN 'Min. £1000'
                WHEN json_extract(finances, '$[0].spending') >= 316 THEN 'Min. £316'
                WHEN json_extract(finances, '$[0].spending') >= 100 THEN 'Min. £100'
                WHEN json_extract(finances, '$[0].spending') >= 32 THEN 'Min. £32'
                WHEN json_extract(finances, '$[0].spending') >= 10 THEN 'Min. £10'
                WHEN json_extract(finances, '$[0].spending') >= 3 THEN 'Min. £3'
                WHEN json_extract(finances, '$[0].spending') >= 1 THEN 'Min. £1'
                ELSE NULL END AS name,
            count(*) AS count,
            sum(json_extract(finances, '$[0].spending')) AS sum
        FROM charity c
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
    last_updated: str


def fetch_all_charities() -> Optional[AllCharitiesResult]:
    db: Database = Database(current_app.config["DB_LOCATION"])
    for row in db["stats"].rows:
        return AllCharitiesResult(
            total_income=row["total_income"],
            total_charities=row["total_charities"],
            last_updated=row["last_updated"],
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
) -> CharityLookupResult:
    db: Database = Database(current_app.config["DB_LOCATION"])
    where_conditions: list[str] = ["1=1"]
    where_args = {}

    if countries:
        for i, country in enumerate(countries):
            country_arg = f"country{i}"
            or_conditions = []
            or_conditions.append(
                f"EXISTS (SELECT 1 FROM json_each(countries) WHERE value = :{country_arg})"
            )
            where_args[country_arg] = country.iso2
        where_conditions.append("(" + " OR ".join(or_conditions) + ")")

        where_conditions.append("json_array_length(countries) <= :max_countries")
        where_args["max_countries"] = getattr(filters, "max_countries", 50)

    if ids:
        where_conditions.append("id IN :ids")
        where_args["ids"] = tuple(ids)

    if filters:
        if filters.search:
            where_conditions.append(
                "charity.id IN (SELECT charity_fts.id FROM charity_fts(:search))"
            )
            where_args["search"] = filters.search

        for c in CLASSIFICATION.keys():
            if getattr(filters, c, None):
                for i, value in enumerate(getattr(filters, c, [])):
                    value_arg = f"{c}{i}"
                    or_conditions = []
                    or_conditions.append(
                        f"EXISTS (SELECT 1 FROM json_each({c}) WHERE value = :{value_arg})"
                    )
                    where_args[value_arg] = value
                where_conditions.append("(" + " OR ".join(or_conditions) + ")")

        if filters.max_income:
            where_conditions.append(
                "json_extract(finances, '$[0].income') <= :max_income"
            )
            where_args["max_income"] = filters.max_income
        if filters.min_income:
            where_conditions.append(
                "json_extract(finances, '$[0].income') >= :min_income"
            )
            where_args["max_income"] = filters.min_income

        if filters.countries:
            for i, country in enumerate(filters.countries):
                country_arg = "country{}".format(i)
                or_conditions = []
                or_conditions.append(
                    f"EXISTS (SELECT 1 FROM json_each(countries) WHERE value = :{country_arg})"
                )
                where_args[country_arg] = country
            where_conditions.append("(" + " OR ".join(or_conditions) + ")")

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
                "NOT EXISTS (SELECT 1 FROM json_each(operations) WHERE json_extract(value, '$.id') = :exclude_grantmakers)"
            )
            where_args["exclude_grantmakers"] = "302"

        if filters.exclude_religious:
            where_conditions.append(
                "NOT EXISTS (SELECT 1 FROM json_each(causes) WHERE json_extract(value, '$.id') = :exclude_religious)"
            )
            where_args["exclude_religious"] = "108"

    where_str = " AND ".join(where_conditions)
    inflation: dict[str, float] = {
        row["year"]: float(row["value"]) for row in db["inflation"].rows
    }

    charities = [
        CharityLookupCharity.from_db(record, all_finances, inflation)
        for record in db["charity"].rows_where(
            where=where_str,
            where_args=where_args,
            limit=limit,
            offset=skip,
            order_by=SORT_OPTIONS.get(sort, SORT_OPTIONS["default"]),
        )
    ]

    result = CharityLookupResult(
        count=db["charity"].count_where(where=where_str, where_args=where_args),
        list_=charities,
    )

    if query == "charity_aggregation":
        result.aggregate = ResultAggregate()

        for row in db.query(
            AGGREGATE_SQL["latestSpending"].format(where_str=where_str), where_args
        ):
            result.aggregate.finances.latestSpending.append(ResultBucket(**row))
        for op_type in ["causes", "beneficiaries", "operations"]:
            for row in db.query(
                AGGREGATE_SQL["causes"].format(where_str=where_str, op_type=op_type),
                where_args,
            ):
                row["key"] = str(row["key"])
                row["name"] = CLASSIFICATION[op_type][row["key"]]
                getattr(result.aggregate, op_type, []).append(ResultBucket(**row))
        for row in db.query(
            AGGREGATE_SQL["countries"].format(where_str=where_str), where_args
        ):
            result.aggregate.areas.append(ResultBucket(**row))
        for row in db.query(
            AGGREGATE_SQL["region"].format(where_str=where_str), where_args
        ):
            result.aggregate.geo.region.append(ResultBucket(**row))
        for row in db.query(
            AGGREGATE_SQL["uk_country"].format(where_str=where_str), where_args
        ):
            result.aggregate.geo.country.append(ResultBucket(**row))

    return result


class OipaItem(TypedDict):
    ref: str
    name: str
    count: int


@dataclass
class OipaItemOrg:
    ref: str
    name: str
    count: int
    country: Optional[Country] = None


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

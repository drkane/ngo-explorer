import csv
import os
import random
from typing import Iterable

import psycopg
import requests
import sqlite_utils
from flask import current_app
from psycopg.rows import dict_row
from sqlite_utils import Database
from tqdm import tqdm

COUNTRIES_CSV = os.path.join(os.path.dirname(__file__), "../utils/countries.csv")
CHARITY_SQL = os.path.join(
    os.path.dirname(__file__), "../utils/queries/charity_list{}.sql"
)
INFLATION_URL = (
    "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l522/mm23/data"
)


def fetch_inflation() -> dict[str, float]:
    r = requests.get(INFLATION_URL)
    data = r.json()
    return {i["year"]: float(i["value"]) for i in data["years"]}


def insert_into_table(db: Database, table_name: str, data: Iterable, pk: str = "id"):
    print(f"Inserting into {table_name} table")
    table = db.table(table_name, pk=pk)
    if not isinstance(table, sqlite_utils.db.Table):
        raise ValueError(f"Error creating {table_name} table")
    table.insert_all(data)
    print(f"Inserted {table.count:,} records into {table_name} table")
    return table


def fetch_ftc(sample=None):
    new_filename = os.path.join(current_app.config["DATA_CONTAINER"], "_temp_new_db.db")
    print(f"Creating new database at {new_filename}")
    db = Database(new_filename, recreate=True)

    insert_into_table(
        db,
        "inflation",
        [{"year": year, "value": value} for year, value in fetch_inflation().items()],
        pk="year",
    )

    with open(COUNTRIES_CSV) as csv_input:
        reader = csv.DictReader(csv_input)
        insert_into_table(
            db,
            "countries",
            reader,
            pk="id",
        )

    with psycopg.connect(
        current_app.config["FTC_DB_URL"],
        row_factory=dict_row,  # type: ignore
    ) as conn:
        with conn.cursor() as cur:
            print("Fetching geolookups")
            cur.execute(
                """
                SELECT "geoCode", "name"
                FROM geo_geolookup
                """
            )
            geolookups = {
                row["geoCode"]: row["name"] for row in tqdm(cur, desc="Geolookups")
            }

            with open(CHARITY_SQL.format("")) as sql_query_file:
                sql_query = sql_query_file.read()
                print("Executing main SQL query")
                cur.execute(sql_query)  # type: ignore

            rows = list(tqdm(cur, desc="Fetching charities", unit=" charity"))
            charity_ids = []
            result = {}
            if sample:
                for row in random.sample(rows, sample):
                    charity_ids.append(f"GB-CHC-{row['id']}")
                    result[row["id"]] = row
            else:
                for row in rows:
                    charity_ids.append(f"GB-CHC-{row['id']}")
                    result[row["id"]] = row

            for sql_query_part, fields in [
                ("_all_finances", ["all_finances"]),
                ("_areas", ["areas"]),
                ("_classification", ["operations", "causes", "beneficiaries"]),
                ("_location", ["geo"]),
            ]:
                with open(CHARITY_SQL.format(sql_query_part)) as sql_query_file:
                    sql_query = sql_query_file.read()
                    print(f"Executing SQL query for {sql_query_part}")
                    cur.execute(sql_query, params={"charity_ids": charity_ids})  # type: ignore
                    for row in tqdm(
                        cur, desc=f"Fetching {sql_query_part}", unit=" charity"
                    ):
                        id = row["charity_id"].removeprefix("GB-CHC-")
                        if id in result:
                            for field in fields:
                                if field == "geo":
                                    for areatype in [
                                        "region",
                                        "country",
                                        "admin_county",
                                        "admin_district",
                                        "admin_ward",
                                        "lsoa",
                                        "msoa",
                                        "parliamentary_constituency",
                                    ]:
                                        row[field][areatype] = geolookups.get(
                                            row[field]
                                            .get("codes", {})
                                            .get(areatype, None),
                                            None,
                                        )
                                result[id][field] = row[field]

            charity_table = insert_into_table(
                db,
                "charity",
                result.values(),
                pk="id",
            )
            charity_table.enable_fts(["id", "name", "activities"])

            cur.execute("""
            SELECT SUM(income) AS total_income,
                COUNT(*) AS total_charities,
                NOW() AS last_updated
            FROM
                charity_charity c
            WHERE
                c."source" = 'ccew'
                AND c."active"
            """)
            insert_into_table(
                db,
                "stats",
                tqdm(cur),
                pk="id",
            )

    # Close the current database
    print("Closing current database")
    db.close()

    # Move the new database to the correct location
    print(f"Moving new database to {current_app.config['DB_LOCATION']}")
    os.replace(new_filename, current_app.config["DB_LOCATION"])

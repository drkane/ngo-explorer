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
    os.path.dirname(__file__), "../utils/queries/charity_list.sql"
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
            with open(CHARITY_SQL) as sql_query_file:
                sql_query = sql_query_file.read()
                cur.execute(sql_query)  # type: ignore

            if sample:
                rows = list(tqdm(cur))
                result = random.sample(rows, sample)
            else:
                result = tqdm(cur)

            charity_table = insert_into_table(
                db,
                "charity",
                result,
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

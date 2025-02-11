import os

import psycopg
import requests
import sqlite_utils
from flask import current_app
from psycopg.rows import dict_row
from sqlite_utils import Database
from tqdm import tqdm


def fetch_inflation() -> dict[str, float]:
    url = "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l522/mm23/data"
    r = requests.get(url)
    data = r.json()
    return {i["year"]: float(i["value"]) for i in data["years"]}


def fetch_ftc():
    with open(
        os.path.join(os.path.dirname(__file__), "../utils/queries/charity_list.sql")
    ) as sql_query_file:
        sql_query = sql_query_file.read()
        db = Database(current_app.config["DB_LOCATION"], recreate=True)
        inflation_table = db.table("inflation", pk="year")
        if not isinstance(inflation_table, sqlite_utils.db.Table):
            raise ValueError("Error creating inflation table")
        inflation_table.insert_all(
            [
                {"year": year, "value": value}
                for year, value in fetch_inflation().items()
            ],
        )

        with psycopg.connect(
            current_app.config["FTC_DB_URL"],
            row_factory=dict_row,  # type: ignore
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query)  # type: ignore

                charity_table = db.table("charity", pk="id")
                if not isinstance(charity_table, sqlite_utils.db.Table):
                    raise ValueError("Error creating charity table")
                charity_table.insert_all(tqdm(cur))
                charity_table.enable_fts(["id", "name"])

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
                stats_table = db.table("stats", pk="id")
                if not isinstance(stats_table, sqlite_utils.db.Table):
                    raise ValueError("Error creating stats table")
                stats_table.insert_all(tqdm(cur))

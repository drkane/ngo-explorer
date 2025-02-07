import os

import psycopg
from flask import current_app
from psycopg.rows import dict_row
from sqlite_utils import Database
from tqdm import tqdm

from ngo_explorer.utils.inflation import fetch_inflation


def fetch_ftc():
    with open(
        os.path.join(os.path.dirname(__file__), "../utils/queries/charity_list.sql")
    ) as sql_query_file:
        sql_query = sql_query_file.read()
        db = Database(current_app.config["DB_LOCATION"], recreate=True)
        db["inflation"].insert_all(
            [
                {"year": year, "value": value}
                for year, value in fetch_inflation().items()
            ],
            pk="year",
        )

        with psycopg.connect(
            current_app.config["FTC_DB_URL"], row_factory=dict_row
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query)
                db["charity"].insert_all(tqdm(cur), pk="id")
                db["charity"].enable_fts(["name"])

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
                db["stats"].insert_all(tqdm(cur))

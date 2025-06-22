import csv
import json
import os


def clean_row(row):
    for f in row:
        if row[f] == "":
            row[f] = None
        if f in ["latitude", "longitude"]:
            try:
                row[f] = float(row[f])
            except (ValueError, TypeError):
                print(f"Invalid value for {f}: {row}")
                continue
    return row


def update_countries():
    with open(
        os.path.join(os.path.dirname(__file__), "../utils/countries.csv"),
        "r",
        encoding="utf-8",
    ) as csv_input:
        with open(
            os.path.join(os.path.dirname(__file__), "../utils/countries.json"),
            "w",
            encoding="utf-8",
        ) as output:
            reader = csv.DictReader(csv_input)
            json.dump({"countries": [clean_row(r) for r in reader]}, output, indent=4)

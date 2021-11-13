import csv
import json
import os


def clean_row(row):
    for f in row:
        if row[f] == "":
            row[f] = None
        if f in ["latitude", "longitude"]:
            row[f] = float(row[f])
    return row


def update_countries():
    with open(
        os.path.join(os.path.dirname(__file__), "../utils/countries.csv")
    ) as csv_input:
        with open(
            os.path.join(os.path.dirname(__file__), "../utils/countries.json"), "w"
        ) as output:
            reader = csv.DictReader(csv_input)
            json.dump({"countries": [clean_row(r) for r in reader]}, output, indent=4)

import json
import os

from flask import url_for
from slugify import slugify

with open(os.path.join(os.path.dirname(__file__), 'countries.json')) as a:
    COUNTRIES = sorted(json.load(a)["countries"], key=lambda k: k['name'])
    COUNTRIES = [c for c in COUNTRIES if c["iso"]!='GBR']

def get_country_groups(as_dict=False):
    continents = set()
    undp = set()
    dac = set()
    for c in COUNTRIES:
        continents.add(c["continent"])
        if c['undp']:
            undp.add(c['undp'])
        if c['dac_status']:
            dac.add(c['dac_status'])

    if as_dict:
        areas = {}
        areas["all"] = {
            "name": "All countries",
            "countries": COUNTRIES
        }
        for c in COUNTRIES:
            areas[slugify(c["iso"])] = {
                "name": c["name"],
                "countries": [c]
            }

        for con in continents:
            areas[("continent", slugify(con))] = {
                "name": con,
                "countries": [c for c in COUNTRIES if c["continent"] == con]
            }

        for i in [("undp", "undp", "All UNDP countries", undp), ("dac", "dac_status", "All DAC countries", dac)]:
            areas[(i[0], "all")] = {
                "name": i[1],
                "countries": [c for c in COUNTRIES if c[i[1]]]
            }
            for con in i[3]:
                areas[(i[0], slugify(con))] = {
                    "name": con,
                    "countries": [c for c in COUNTRIES if c[i[1]] == con]
                }
        return areas

    return [
        (None, [{"id": url_for("data.country", countryid="all"), "name": "All countries"}]),
        ("Continents", [
            {"id": url_for("data.region", regiontype="continent", regionid= slugify(c)), "name": c} for c in continents
        ]),
        ("UNDP", [
            {"id": url_for("data.region", regiontype="undp", regionid="all"), "name": "All groups"}
        ] + [
            {"id": url_for("data.region", regiontype="undp", regionid=slugify(c)), "name": c} for c in undp if c
        ]),
        ("DAC", [
            {"id": url_for("data.region", regiontype="dac", regionid="all"), "name": "All groups"}
        ] + [
            {"id": url_for("data.region", regiontype="dac", regionid=slugify(c)), "name": c} for c in dac if c
        ]),
    ] + [
        (con, [
            {"id": url_for("data.country", countryid=slugify(c["iso"])), "name": c["name"]}
            for c in COUNTRIES if c["continent"] == con
        ])
        for con in sorted(continents)
    ]


def get_multiple_countries(countryid):
    countryids = countryid.lower().split("+")
    area = {
        "name": [],
        "countries": []
    }
    for i in countryids:
        this_area = get_country_groups(as_dict=True).get(i)
        area["name"].append(this_area["name"])
        area["countries"].extend(this_area["countries"])
    area["name"] = ", ".join(area["name"])
    return area

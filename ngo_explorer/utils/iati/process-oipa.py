import json
import os

# @TODO: turn in flask command line script

with open(
    os.path.join(os.path.dirname(__file__), "oipa-country-participant.json"),
    encoding="utf8",
) as a:
    data = json.load(a)
    countries = {}
    print(data["count"])
    for r in data["results"]:
        country_code = r.get("recipient_country", {}).get("code")
        orgid = r.get("participating_organisation_ref", "").strip()
        if country_code not in countries:
            countries[country_code] = {}

        if orgid.startswith("GB-C"):
            if orgid not in countries[country_code]:
                countries[country_code][orgid] = {
                    "ref": orgid,
                    "name": r.get("participating_organisation"),
                    "count": 0,
                }

            countries[country_code][orgid]["count"] += r.get("count", 0)

    for country_code in countries.keys():
        countries[country_code] = list(countries[country_code].values())

    with open(
        os.path.join(os.path.dirname(__file__), "oipa-country-participant-gb.json"),
        "w",
        encoding="utf8",
    ) as b:
        json.dump(countries, b, indent=4)
    for c, orgs in countries.items():
        print(c, len(orgs))

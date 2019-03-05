import io
import csv
import json

from flask import current_app, Response
import xlsxwriter
from slugify import slugify

from .utils import record_to_nested, nested_to_record
from .filters import CLASSIFICATION
from .fetchdata import fetch_charitybase

DOWNLOAD_OPTIONS = {
    "main": {
        "options": [
            {'label': 'Charity number', 'value': 'id', 'checked': True},
            {'label': 'Charity name', 'value': 'name', 'checked': True},
            # {'label': 'Governing document', 'value': 'governingDoc'},
            {'label': 'Description of activities',
             'value': 'activities'},
            # {'label': 'Charitable objects', 'value': 'objectives'},
            {'label': 'Causes served', 'value': 'causes'},
            {'label': 'Beneficiaries', 'value': 'beneficiaries'},
            {'label': 'Activities', 'value': 'operations'},
        ],
        "name": "Charity information"
    },
    "financial": {
        "options": [
            {'label': 'Latest income', 'value': 'income.latest.total', 'checked': True},
            {'label': 'Latest income date', 'value': 'income.latest.date', 'checked': True},
            # {'label': 'Company number', 'value': 'companiesHouseNumber'},
            # {'label': 'Financial year end', 'value': 'fyend'},
            # {'label': 'Number of trustees',
            #  'value': 'people.trustees'},
            # {'label': 'Number of employees',
            #  'value': 'people.employees'},
            # {'label': 'Number of volunteers',
            #  'value': 'people.volunteers'},
        ],
        "name": "Financial"
    },
    "contact": {
        "options": [
            {'label': 'Email', 'value': 'contact.email'},
            {'label': 'Website', 'value': 'website'},
            {'label': 'Address', 'value': 'contact.address'},
            {'label': 'Postcode', 'value': 'contact.postcode'},
            {'label': 'Phone number', 'value': 'contact.phone'},
        ],
        "name": "Contact details"
    },
    "geo": {
        "options": {
            "aoo": [
                # {'label': 'Description of area of benefit', 'value': 'areaOfBenefit'},
                {'label': 'Area of operation',
                 'value': 'areas'},
                {'label': 'Countries where this charity operates',
                 'value': 'countries'},
            ],
            "geo": [
                {'label': 'Country', 'value': 'geo.country'},
                {'label': 'Region', 'value': 'geo.region'},
                {'label': 'County', 'value': 'geo.admin_county'},
                {'label': 'County [code]',
                 'value': "geo.codes.admin_county"},
                {'label': 'Local Authority',
                 'value': 'geo.admin_district'},
                {'label': 'Local Authority [code]',
                 'value': "geo.codes.admin_district"},
                {'label': 'Ward', 'value': 'geo.admin_ward'},
                {'label': 'Ward [code]',
                 'value': 'geo.codes.admin_ward'},
                {'label': 'Parish', 'value': 'geo.parish'},
                {'label': 'Parish [code]',
                 'value': 'geo.codes.parish'},
                {'label': 'LSOA', 'value': 'geo.lsoa'},
                {'label': 'MSOA', 'value': 'geo.msoa'},
                {'label': 'Parliamentary Constituency',
                 'value': 'geo.parliamentary_constituency'},
                {'label': 'Parliamentary Constituency [code]',
                 'value': 'geo.codes.parliamentary_constituency'},
            ],
        },
        "description": "The following fields are based on the postcode of the charities' UK registered office",
        "name": "Geography fields"
    },
}


def parse_download_fields(fields):
    fields = record_to_nested(fields)

    # add in country and area fields
    if "countries" in fields or "areas" in fields:
        fields["areas"] = {
            "id": {},
            "name": {}
        }
        del fields["countries"]
    
    # add proper formating for the classification fields
    for c in CLASSIFICATION.keys():
        if c in fields:
            fields[c] = {
                "id": {},
                "name": {}
            }

    # ID and name field always returned
    fields["id"] = {}
    fields["name"] = {}

    return fields


def download_file(area, filters, fields, filetype='csv', max_results=500):
    countries = area["countries"]
    limit = 30
    cb_variables = dict(
        filters=filters,
        limit=limit,
        skip=0,
        query="charity_download",
        query_fields=parse_download_fields(fields)
    )

    raw_results = fetch_charitybase(countries, **cb_variables)
    # check here if query has failed

    charity_list = raw_results["list"]

    stop_searching = min(
        [raw_results["count"], current_app.config['DOWNLOAD_LIMIT']])
    cb_variables['skip'] += limit
    while cb_variables['skip'] < stop_searching:
        raw_results = fetch_charitybase(countries, **cb_variables)
        charity_list.extend(raw_results["list"])
        cb_variables['skip'] += limit

    if filetype.lower() in ["excel", "xlsx", "xls"]:
        filetype = 'xlsx'
    else:
        filetype = filetype.lower()

    results = []
    for r in charity_list:
        if "countries" in fields:
            r["countries"] = [a for a in r.get(
                "areas", []) if a["id"].startswith("D-")]
            if "areas" not in fields:
                del r["areas"]

        if "areas" in fields:
            r["areas"] = [a for a in r.get(
                "areas", []) if not a["id"].startswith("D-")]

        if filetype in ["xlsx", "csv"]:
            r = nested_to_record(r)
            # r = {k: r.get(k) for k in fields}
            for k, v in r.items():
                if isinstance(v, list):
                    if v and isinstance(v[0], dict):
                        v = [i.get("name", list(i.values())[0]) for i in v]
                    r[k] = ";".join(v)
        results.append(r)

    fieldnames = ["id", "name"] + \
        sorted([v for v in fields if v not in ["id", "name"]])

    output = io.StringIO()
    if filetype == 'json':
        json.dump(results, output, indent=4)
        mimetype = 'application/json'
        extension = 'json'

    elif filetype == 'jsonl':
        for c in results:
            output.write(json.dumps(c) + "\n")
        mimetype = 'application/x-jsonlines'
        extension = 'jsonl'

    elif filetype == 'xlsx':
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        worksheet.write_row(0, 0, fieldnames)
        row = 1
        for c in results:
            vals = [c.get(f) for f in fieldnames]
            worksheet.write_row(row, 0, vals)
            row += 1
        workbook.close()
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        extension = 'xlsx'

    else:  # assume csv if not given
        writer = csv.DictWriter(output, fieldnames=list(fieldnames))
        writer.writeheader()
        for c in results:
            writer.writerow(c)
        mimetype = 'text/csv'
        extension = 'csv'

    filename = "ngoexplorer-{}".format(slugify(area["name"]))

    return Response(
        output.getvalue(),
        mimetype=mimetype,
        headers={
            "Content-disposition": "attachment; filename={}.{}".format(filename, extension)
        }
    )

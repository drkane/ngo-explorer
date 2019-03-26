import io
import csv
import json

from flask import current_app, Response
from flask_babel import _
import xlsxwriter
from slugify import slugify

from .utils import record_to_nested
from .filters import CLASSIFICATION
from .fetchdata import fetch_charitybase

DOWNLOAD_OPTIONS = {
    "main": {
        "options": [
            {'label': _('Charity number'), 'value': 'id', 'checked': True},
            {'label': _('Charity name'), 'value': 'name', 'checked': True},
            {'label': _('Governing document'), 'value': 'governingDoc'},
            {'label': _('Description of activities'),
             'value': 'activities'},
            {'label': _('Charitable objects'), 'value': 'objectives'},
            {'label': _('Causes served'), 'value': 'causes'},
            {'label': _('Beneficiaries'), 'value': 'beneficiaries'},
            {'label': _('Activities'), 'value': 'operations'},
        ],
        "name": _("Charity information")
    },
    "financial": {
        "options": [
            {'label': _('Latest income'), 'value': 'income.latest.total', 'checked': True},
            {'label': _('Latest income date'), 'value': 'income.latest.date', 'checked': True},
            {'label': _('Income history'), 'value': 'income.history', 'checked': False},
            {'label': _('Spending history'), 'value': 'spending.history', 'checked': False},
            {'label': _('Inflation adjust income/spending history'), 'value': 'inflation_adjusted', 'checked': False},
            # {'label': _('Company number'), 'value': 'companiesHouseNumber'},
            # {'label': _('Financial year end'), 'value': 'fyend'},
            {'label': _('Number of trustees'),
             'value': 'numPeople.trustees'},
            {'label': _('Number of employees'),
             'value': 'numPeople.employees'},
            {'label': _('Number of volunteers'),
             'value': 'numPeople.volunteers'},
        ],
        "description": _("""Financial data can be adjusted to consistent prices using the
        <a href="https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l522/mm23" target="_blank" class="link blue external-link">consumer price inflation (CPIH)</a>
        measure published by the Office for National Statistics."""),
        "name": "Financial"
    },
    "contact": {
        "options": [
            {'label': _('Email'), 'value': 'contact.email'},
            {'label': _('Website'), 'value': 'website'},
            {'label': _('Address'), 'value': 'contact.address'},
            {'label': _('Postcode'), 'value': 'contact.postcode'},
            {'label': _('Phone number'), 'value': 'contact.phone'},
        ],
        "name": _("Contact details")
    },
    "geo": {
        "options": {
            "aoo": [
                {'label': _('Description of area of benefit'), 'value': 'areaOfBenefit'},
                {'label': _('Area of operation'),
                 'value': 'areas'},
                {'label': _('Countries where this charity operates'),
                 'value': 'countries'},
            ],
            "geo": [
                {'label': _('Country'), 'value': 'geo.country'},
                {'label': _('Region'), 'value': 'geo.region'},
                {'label': _('County'), 'value': 'geo.admin_county'},
                {'label': _('County [code]'),
                 'value': "geo.codes.admin_county"},
                {'label': _('Local Authority'),
                 'value': 'geo.admin_district'},
                {'label': _('Local Authority [code]'),
                 'value': "geo.codes.admin_district"},
                {'label': _('Ward'), 'value': 'geo.admin_ward'},
                {'label': _('Ward [code]'),
                 'value': 'geo.codes.admin_ward'},
                {'label': _('Parish'), 'value': 'geo.parish'},
                {'label': _('Parish [code]'),
                 'value': 'geo.codes.parish'},
                {'label': _('LSOA'), 'value': 'geo.lsoa'},
                {'label': _('MSOA'), 'value': 'geo.msoa'},
                {'label': _('Parliamentary Constituency'),
                 'value': 'geo.parliamentary_constituency'},
                {'label': _('Parliamentary Constituency [code]'),
                 'value': 'geo.codes.parliamentary_constituency'},
            ],
        },
        "description": _("The following fields are based on the postcode of the charities' UK registered office"),
        "name": _("Geography fields")
    },
}


def parse_download_fields(original_fields):

    fields = record_to_nested(original_fields)

    # get income fields
    finances = None
    if "income.history" in original_fields or "spending.history" in original_fields:
        finances_key = "finances(all:true)"
        finances = {"financialYear": {"end": {}}}
        if "income.history" in original_fields:
            finances["income"] = {}
            del fields["income"]
        if "spending.history" in original_fields:
            finances["spending"] = {}
            del fields["spending"]
    elif "income.latest.total" in original_fields or "income.latest.date" in original_fields:
        finances_key = "finances"
        finances = {}
        if "income.latest.total" in original_fields:
            finances["income"] = {}
        if "income.latest.date" in original_fields:
            finances["financialYear"] = {"end": {}}
        del fields["income"]

    if finances:
        fields[finances_key] = finances

    if "inflation_adjusted" in fields:
        del fields["inflation_adjusted"]

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
    fields["names"] = {
        "value": {},
        "primary": {}
    }
    fields["name"] = {}

    return fields


def download_file(area, filters, fields, filetype='csv', max_results=500):
    limit = 30
    cb_variables = dict(
        filters=filters,
        limit=limit,
        skip=0,
        query="charity_download",
        query_fields=parse_download_fields(fields)
    )

    if "ids" in area:
        # assume it's a list of ids
        cb_variables["ids"] = area["ids"]
    elif "countries" in area:
        # assume it's an "Area" object with countries in
        cb_variables["countries"] = area["countries"]

    raw_results = fetch_charitybase(**cb_variables)
    # check here if query has failed

    charity_list = raw_results.list

    stop_searching = min(
        [raw_results.count, current_app.config['DOWNLOAD_LIMIT']])
    cb_variables['skip'] += limit
    while cb_variables['skip'] < stop_searching:
        raw_results = fetch_charitybase(**cb_variables)
        charity_list.extend(raw_results.list)
        cb_variables['skip'] += limit

    if filetype.lower() in ["excel", "xlsx", "xls"]:
        filetype = 'xlsx'
    else:
        filetype = filetype.lower()

    results = []
    fieldnames_ = set()
    for r in charity_list:
        if filetype in ["xlsx", "csv"]:
            result = r.as_flat_dict()
        else:
            result = r.as_dict()
        results.append(result)
        fieldnames_.update(result.keys())

    fieldnames = ["id", "name"] + \
        sorted([v for v in fieldnames_ if v not in ["id", "name"] and not v.startswith("income_") and not v.startswith("spending_")]) + \
        sorted([v for v in fieldnames_ if v.startswith("income_") or v.startswith("spending_")])

    # check for fields that can end up in the output without being asked for
    for f in ["countries", "areas", "names"]:
        if f not in fields and f in fieldnames:
            fieldnames.remove(f)

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
            writer.writerow({f: c.get(f) for f in fieldnames})
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

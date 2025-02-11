import csv
import io
import json
from dataclasses import dataclass
from typing import Optional

import xlsxwriter
from flask import Response
from flask_babel import _
from slugify import slugify

from ngo_explorer.utils.countries import (
    CountryGroupItem,
    CountryGroupItemList,
    CountryGroupItemUpload,
)
from ngo_explorer.utils.fetchdata import fetch_charity_details
from ngo_explorer.utils.filters import CLASSIFICATION, Filters
from ngo_explorer.utils.utils import record_to_nested


@dataclass
class DownloadOption:
    label: str
    value: str
    checked: bool = False


@dataclass
class DownloadOptionGroup:
    options: list[DownloadOption] | dict[str, list[DownloadOption]]
    name: str
    description: Optional[str] = None


DOWNLOAD_OPTIONS: dict[str, DownloadOptionGroup] = {
    "main": DownloadOptionGroup(
        options=[
            DownloadOption(label=_("Charity number"), value="id", checked=True),
            DownloadOption(label=_("Charity name"), value="name", checked=True),
            DownloadOption(
                label=_("Registration date"),
                value="registrationDate",
                checked=True,
            ),
            DownloadOption(label=_("Governing document"), value="governingDoc"),
            DownloadOption(label=_("Description of activities"), value="activities"),
            DownloadOption(label=_("Charitable objects"), value="objectives"),
            DownloadOption(label=_("Causes served"), value="causes"),
            DownloadOption(label=_("Beneficiaries"), value="beneficiaries"),
            DownloadOption(label=_("Activities"), value="operations"),
        ],
        name=_("Charity information"),
    ),
    "financial": DownloadOptionGroup(
        options=[
            DownloadOption(
                label=_("Latest income"),
                value="income.latest.total",
                checked=True,
            ),
            DownloadOption(
                label=_("Latest income date"),
                value="income.latest.date",
                checked=True,
            ),
            DownloadOption(
                label=_("Income history"), value="income.history", checked=False
            ),
            DownloadOption(
                label=_("Spending history"),
                value="spending.history",
                checked=False,
            ),
            DownloadOption(
                label=_("Inflation adjust income/spending history"),
                value="inflation_adjusted",
                checked=False,
            ),
            # DownloadOption(label=_('Company number'), value='companiesHouseNumber'),
            # DownloadOption(label=_('Financial year end'), value='fyend'),
            DownloadOption(label=_("Number of trustees"), value="numPeople.trustees"),
            DownloadOption(label=_("Number of employees"), value="numPeople.employees"),
            DownloadOption(
                label=_("Number of volunteers"), value="numPeople.volunteers"
            ),
        ],
        description=_(
            """Financial data can be adjusted to consistent prices using the
        <a href="https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l522/mm23" target="_blank" class="link blue external-link">consumer price inflation (CPIH)</a>
        measure published by the Office for National Statistics."""
        ),
        name="Financial",
    ),
    "contact": DownloadOptionGroup(
        options=[
            DownloadOption(label=_("Email"), value="contact.email"),
            DownloadOption(label=_("Website"), value="website"),
            DownloadOption(label=_("Address"), value="contact.address"),
            DownloadOption(label=_("Postcode"), value="contact.postcode"),
            DownloadOption(label=_("Phone number"), value="contact.phone"),
        ],
        name=_("Contact details"),
    ),
    "geo": DownloadOptionGroup(
        options={
            "aoo": [
                DownloadOption(
                    label=_("Description of area of benefit"),
                    value="areaOfBenefit",
                ),
                DownloadOption(label=_("Area of operation"), value="areas"),
                DownloadOption(
                    label=_("Countries where this charity operates"),
                    value="countries",
                ),
            ],
            "geo": [
                DownloadOption(label=_("Country"), value="geo.country"),
                DownloadOption(label=_("Region"), value="geo.region"),
                DownloadOption(label=_("County"), value="geo.admin_county"),
                DownloadOption(
                    label=_("County [code]"), value="geo.codes.admin_county"
                ),
                DownloadOption(label=_("Local Authority"), value="geo.admin_district"),
                DownloadOption(
                    label=_("Local Authority [code]"),
                    value="geo.codes.admin_district",
                ),
                DownloadOption(label=_("Ward"), value="geo.admin_ward"),
                DownloadOption(label=_("Ward [code]"), value="geo.codes.admin_ward"),
                # DownloadOption(label=_("Parish"), value="geo.parish"),
                # DownloadOption(label=_("Parish [code]"), value="geo.codes.parish"),
                DownloadOption(label=_("LSOA"), value="geo.lsoa"),
                DownloadOption(label=_("MSOA"), value="geo.msoa"),
                DownloadOption(
                    label=_("Parliamentary Constituency"),
                    value="geo.parliamentary_constituency",
                ),
                DownloadOption(
                    label=_("Parliamentary Constituency [code]"),
                    value="geo.codes.parliamentary_constituency",
                ),
            ],
        },
        description=_(
            "The following fields are based on the postcode of the charities' UK registered office"
        ),
        name=_("Geography fields"),
    ),
}


def parse_download_fields(original_fields: list[str]):
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
    elif (
        "income.latest.total" in original_fields
        or "income.latest.date" in original_fields
    ):
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
        fields["areas"] = {"id": {}, "name": {}}
        del fields["countries"]

    # add proper formating for the classification fields
    for c in CLASSIFICATION.keys():
        if c in fields:
            fields[c] = {"id": {}, "name": {}}

    # ID and name field always returned
    fields["id"] = {}
    fields["names"] = {"value": {}, "primary": {}}
    fields["name"] = {}

    return fields


def download_file(
    area: Optional[CountryGroupItem | CountryGroupItemList | CountryGroupItemUpload],
    filters: Filters,
    fields: list[str],
    ids: Optional[list[str]] = None,
    filetype: str = "csv",
    max_results: int = 500,
):
    fetch_ids = None
    fetch_countries = None
    if ids:
        # assume it's a list of ids
        fetch_ids = ids
    elif isinstance(area, (CountryGroupItemList, CountryGroupItem)):
        # assume it's an "Area" object with countries in
        fetch_countries = area.countries

    raw_results = fetch_charity_details(
        filters=filters,
        limit=max_results,
        skip=0,
        query="charity_download",
        query_fields=parse_download_fields(fields),
        countries=fetch_countries,
        ids=fetch_ids,
    )
    # check here if query has failed

    charity_list = raw_results.list_

    if filetype.lower() in ["excel", "xlsx", "xls"]:
        filetype = "xlsx"
    else:
        filetype = filetype.lower()

    results = []
    fieldnames_ = set()
    if charity_list:
        for r in charity_list:
            if filetype in ["xlsx", "csv"]:
                result = r.as_flat_dict()
            else:
                result = r.as_dict()
            results.append(result)
            fieldnames_.update(result.keys())

    fieldnames = (
        ["id", "name"]
        + sorted(
            [
                v
                for v in fieldnames_
                if v not in ["id", "name"]
                and not v.startswith("income_")
                and not v.startswith("spending_")
            ]
        )
        + sorted(
            [
                v
                for v in fieldnames_
                if v.startswith("income_") or v.startswith("spending_")
            ]
        )
    )

    # check for fields that can end up in the output without being asked for
    for f in ["countries", "areas", "names"]:
        if f not in fields and f in fieldnames:
            fieldnames.remove(f)

    output = io.StringIO()
    if filetype == "json":
        json.dump(results, output, indent=4)
        mimetype = "application/json"
        extension = "json"

    elif filetype == "jsonl":
        for c in results:
            output.write(json.dumps(c) + "\n")
        mimetype = "application/x-jsonlines"
        extension = "jsonl"

    elif filetype == "xlsx":
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
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        extension = "xlsx"

    else:  # assume csv if not given
        writer = csv.DictWriter(output, fieldnames=list(fieldnames))
        writer.writeheader()
        for c in results:
            writer.writerow({f: c.get(f) for f in fieldnames})
        mimetype = "text/csv"
        extension = "csv"

    if area:
        filename = "ngoexplorer-{}".format(slugify(area.name))
    else:
        filename = "ngoexplorer"

    return Response(
        output.getvalue(),
        mimetype=mimetype,
        headers={
            "Content-disposition": "attachment; filename={}.{}".format(
                filename, extension
            )
        },
    )

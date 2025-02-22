from dataclasses import dataclass, field
from typing import Optional

from flask_babel import _
from werkzeug.datastructures import ImmutableMultiDict, MultiDict

CLASSIFICATION = {
    "causes": {
        "101": _("General charitable purposes"),
        "102": _("Education and training"),
        "103": _("Health or saving of lives"),
        "104": _("Disability"),
        "105": _("Relief of poverty"),
        "106": _("Overseas aid/famine relief"),
        "107": _("Accommodation/housing"),
        "108": _("Religious activities"),
        "109": _("Arts/culture/heritage/science"),
        "110": _("Amateur sport"),
        "111": _("Animals"),
        "112": _("Environment/conservation/heritage"),
        "113": _("Economic and community development"),
        "114": _("Armed forces and emergency services"),
        "115": _("Human rights, equality and diversity"),
        "116": _("Recreation"),
        "117": _("Other charitable purposes"),
    },
    "beneficiaries": {
        "201": _("Children/young people"),
        "202": _("Elderly/old people"),
        "203": _("People with disabilities"),
        "204": _("People of a particular ethnic or racial origin"),
        "205": _("Other charities or voluntary bodies"),
        "206": _("Other defined groups"),
        "207": _("The general public/mankind"),
    },
    "operations": {
        "301": _("Makes grants to individuals"),
        "302": _("Makes grants to organisations"),
        "303": _("Provides other finance"),
        "304": _("Provides human resources"),
        "305": _("Provides buildings/facilities/open space"),
        "306": _("Provides services"),
        "307": _("Provides advocacy/advice/information"),
        "308": _("Sponsors or undertakes research"),
        "309": _("Acts as an umbrella or resource body"),
        "310": _("Other charitable activities"),
    },
}

REGIONS = {
    # "E92000001": _("England"),  # Lloegr
    # "K02000001": _("United Kingdom"),  # Y Deyrnas Gyfunol
    # "K03000001": _("Great Britain"),  # Prydain Fawr
    # "K04000001": _("England and Wales"),  # Cymru a Lloegr
    # "N92000002": _("Northern Ireland"),  # Gogledd Iwerddon
    # "S92000003": _("Scotland"),  # Yr Alban
    "W92000004": _("Wales"),  # Cymru
    "E12000001": _("North East"),  # Gogledd Ddwyrain
    "E12000002": _("North West"),  # Gogledd Orllewin
    "E12000003": _("Yorkshire and The Humber"),  # Swydd Efrog a Humber
    "E12000004": _("East Midlands"),  # Dwyrain y Canolbarth
    "E12000005": _("West Midlands"),  # Gorllewin y Canolbarth
    "E12000006": _("East of England"),  # Dwyrain Lloegr
    "E12000007": _("London"),  # Llundain
    "E12000008": _("South East"),  # De Ddwyrain
    "E12000009": _("South West"),  # De Orllewin
}


@dataclass
class Filters:
    search: Optional[str] = None
    causes: list[str] = field(default_factory=list)
    beneficiaries: list[str] = field(default_factory=list)
    operations: list[str] = field(default_factory=list)
    max_income: Optional[int] = None
    min_income: Optional[int] = None
    countries: list[str] = field(default_factory=list)
    regions: Optional[str] = None
    exclude_grantmakers: Optional[bool] = None
    exclude_religious: Optional[bool] = None
    max_countries: Optional[int] = 50
    skip: Optional[int] = None


def parse_filters(
    filters: MultiDict[str, str] | ImmutableMultiDict[str, str],
) -> Filters:
    return_filters = Filters()

    # search
    if filters.get("filter-search"):
        return_filters.search = filters.get("filter-search")
        if (
            isinstance(return_filters.search, str)
            and '"' not in return_filters.search
            and " OR " not in return_filters.search
        ):
            return_filters.search = '"{}"'.format(return_filters.search)

    # cause, beneficiaries, operations
    if filters.get("filter-classification"):
        categories = filters.getlist("filter-classification")
        for i in CLASSIFICATION.keys():
            for j in CLASSIFICATION[i].keys():
                if j in categories:
                    getattr(return_filters, i).append(j)

    # max and min income
    filter_max_income = filters.get("filter-max-income")
    if isinstance(filter_max_income, str):
        try:
            return_filters.max_income = int(filter_max_income)
        except ValueError:
            pass
    filter_min_income = filters.get("filter-min-income")
    if isinstance(filter_min_income, str):
        try:
            return_filters.min_income = int(filter_min_income)
        except ValueError:
            pass

    # further country filter (refines the main url country selection)
    if filters.get("filter-countries"):
        return_filters.countries = filters.getlist("filter-countries")

    # region filter
    if filters.get("filter-regions"):
        return_filters.regions = filters.get("filter-regions")

    # exclude grantmakers
    if "filter-exclude-grantmakers" in filters:
        return_filters.exclude_grantmakers = True

    # exclude grantmakers
    if "filter-exclude-religious" in filters:
        return_filters.exclude_religious = True

    # max_countries
    return_filters.max_countries = int(filters.get("filter-max-countries", 50))

    # page for lists
    filter_skip = filters.get("filter-skip")
    if isinstance(filter_skip, str):
        try:
            return_filters.skip = int(filter_skip)
        except ValueError:
            pass

    return return_filters

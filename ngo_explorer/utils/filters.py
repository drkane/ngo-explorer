from flask_babel import _

CLASSIFICATION = {
    "causes": {
        "101": _("General charitable purposes"),
        "102": _("Education/training"),
        "103": _("The advancement of health or saving of lives"),
        "104": _("Disability"),
        "105": _("The prevention or relief of poverty"),
        "106": _("Overseas aid/famine relief"),
        "107": _("Accommodation/housing"),
        "108": _("Religious activities"),
        "109": _("Arts/culture/heritage/science"),
        "110": _("Amateur sport"),
        "111": _("Animals"),
        "112": _("Environment/conservation/heritage"),
        "113": _("Economic/community development/employment"),
        "114": _("Armed forces/emergency service efficiency"),
        "115": _("Human rights/religious or racial harmony/equality or diversity"),
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
    }
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


def parse_filters(filters):
    return_filters = {}
    
    # search
    if filters.get("filter-search"):
        return_filters["search"] = filters.get("filter-search")
        if '"' not in return_filters["search"] and " OR " not in return_filters["search"]:
            return_filters["search"] = '"{}"'.format(return_filters["search"])

    # cause, beneficiaries, operations
    if filters.get("filter-classification"):
        categories = filters.getlist("filter-classification")
        for i in CLASSIFICATION.keys():
            for j in CLASSIFICATION[i].keys():
                if j in categories:
                    if i not in return_filters:
                        return_filters[i] = []
                    return_filters[i].append(j)

    # max and min income
    if filters.get("filter-max-income"):
        return_filters["max_income"] = int(filters.get("filter-max-income"))
    if filters.get("filter-min-income"):
        return_filters["min_income"] = int(filters.get("filter-min-income"))

    # further country filter (refines the main url country selection)
    if filters.get("filter-countries"):
        return_filters['countries'] = filters.getlist('filter-countries')

    # region filter
    if filters.get("filter-regions"):
        return_filters['regions'] = filters.get('filter-regions')

    # exclude grantmakers
    if "filter-exclude-grantmakers" in filters:
        return_filters['exclude_grantmakers'] = True

    # exclude grantmakers
    if "filter-exclude-religious" in filters:
        return_filters['exclude_religious'] = True

    # max_countries
    return_filters["max_countries"] = int(filters.get("filter-max-countries", 50))

    # page for lists
    if filters.get("filter-skip"):
        return_filters['skip'] = int(filters.get("filter-skip"))

    return return_filters

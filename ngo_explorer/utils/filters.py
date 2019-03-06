
CLASSIFICATION = {
    "causes": {
        "101": "General charitable purposes",
        "102": "Education/training",
        "103": "The advancement of health or saving of lives",
        "104": "Disability",
        "105": "The prevention or relief of poverty",
        "106": "Overseas aid/famine relief",
        "107": "Accommodation/housing",
        "108": "Religious activities",
        "109": "Arts/culture/heritage/science",
        "110": "Amateur sport",
        "111": "Animals",
        "112": "Environment/conservation/heritage",
        "113": "Economic/community development/employment",
        "114": "Armed forces/emergency service efficiency",
        "115": "Human rights/religious or racial harmony/equality or diversity",
        "116": "Recreation",
        "117": "Other charitable purposes"
    },
    "beneficiaries": {
        "201": "Children/young people",
        "202": "Elderly/old people",
        "203": "People with disabilities",
        "204": "People of a particular ethnic or racial origin",
        "205": "Other charities or voluntary bodies",
        "206": "Other defined groups",
        "207": "The general public/mankind"
    },
    "operations": {
        "301": "Makes grants to individuals",
        "302": "Makes grants to organisations",
        "303": "Provides other finance",
        "304": "Provides human resources",
        "305": "Provides buildings/facilities/open space",
        "306": "Provides services",
        "307": "Provides advocacy/advice/information",
        "308": "Sponsors or undertakes research",
        "309": "Acts as an umbrella or resource body",
        "310": "Other charitable activities"
    }
}

# def clean_filters(filters):

#     return {
#         k: v 
#     }


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

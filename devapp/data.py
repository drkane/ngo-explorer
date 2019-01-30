import os

from charitybase import CharityBase

def fetch_charities(filters: dict):
    if not filters.get("regnos") and not filters.get("aoo"):
        return []

    charityBase = CharityBase(apiKey=os.getenv('CHARITYBASE_API_KEY'))

    query = {
        'fields': [
            'income.latest.total',
            'income.annual',
            'areasOfOperation',
            'causes',
            'beneficiaries',
            'operations',
            'contact.geo.region'
        ],
        'sort': 'income.latest.total:desc',
        'limit': 50,
        'skip': 0,
    }

    if filters.get("regnos"):
        query['ids.GB-CHC'] = ",".join(filters.get("regnos"))

    if filters.get("aoo"):
        query['areasOfOperation.id'] = ",".join(filters.get("aoo"))

    if filters.get("search"):
        query['search'] = filters.get("search")

    if filters.get("min_income") or filters.get("max_income"):
        query['incomeRange'] = '{},{}'.format(
            filters.get("min_income", ""),
            filters.get("max_income", "")
        ).replace("None", "")

    causes = filters.get("causes") if filters.get("causes") else []
    if filters.get("include_oa", True) and "106" not in causes:
        causes.append("106")

    if causes:
        query['causes.id'] = ",".join(causes)

    if filters.get("beneficiaries"):
        query['beneficiaries.id'] = ",".join(filters.get("beneficiaries"))

    if filters.get("operations"):
        query['operations.id'] = ",".join(filters.get("operations"))

    print(query)

    res = charityBase.charity.list(query)

    results = []
    for c in res.charities:
        c['countries'] = [
            ctry['name'] for ctry in c['areasOfOperation']
            if ctry['locationType'] == "Country" and ctry['name'] not in ['Scotland', 'Northern Ireland']
        ]
        if len(c['countries']) > filters.get("max_countries", 200):
            continue
        if not c['countries']:
            continue
        results.append(c)

    return results

import os

from charitybase import CharityBase

def fetch_charities(regnos: list, aoo: list, max_countries: int = 200, include_oa: bool = True):
    if not regnos and not aoo:
        return []

    charityBase = CharityBase(apiKey=os.getenv('CHARITYBASE_API_KEY'))

    query = {
        'fields': ['income.latest.total', 'income.annual', 'areasOfOperation'],
        'sort': 'income.latest.total:desc',
        'limit': 50,
        'skip': 0,
    }

    if regnos:
        query['ids.GB-CHC'] = ",".join(regnos)

    if aoo:
        query['areasOfOperation.id'] = ",".join(aoo)

    if include_oa:
        query['causes.id'] = "106"

    print(query)

    res = charityBase.charity.list(query)

    results = []
    for c in res.charities:
        c['countries'] = [
            ctry['name'] for ctry in c['areasOfOperation']
            if ctry['locationType'] == "Country" and ctry['name'] not in ['Scotland', 'Northern Ireland']
        ]
        if len(c['countries']) > max_countries:
            continue
        if not c['countries']:
            continue
        results.append(c)

    return results

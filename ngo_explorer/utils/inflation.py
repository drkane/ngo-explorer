import requests


def fetch_inflation():
    url = "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l522/mm23/data"
    r = requests.get(url)
    data = r.json()
    return {i["year"]: float(i["value"]) for i in data["years"]}

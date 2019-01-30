import datetime

def get_charity_row(c, number_format=True):
    if len(c['countries']) > 10:
        countries = "{:,.0f} countries".format(len(c['countries']))
    else:
        countries = ", ".join(c['countries'])

    income = c.get("income", {}).get(
        "latest", {}).get("total", None)
    if number_format:
        if income is None:
            income = 'Unknown'
        else:
            income = "£{:,.0f}".format(float(income))

    return {
        "Charity Number": c.get("ids", {}).get("GB-CHC", "Unknown"),
        # @TODO: currently DataTable doesn't support HTML in cells
        # "Name": html.A(
        #     href='https://charitybase.uk/charities/{}'.format(
        #         c.get("ids", {}).get("GB-CHC", "Unknown")),
        #     children=c.get("name", "Unknown"),
        #     target="_blank"
        # ),
        "Name": c.get("name", "Unknown"),
        "Income": income,
        "Countries of operation": countries
    }

def date_to_financial_year(datevalue, month_end=4):
    d = datetime.datetime.strptime(datevalue, "%Y-%m-%d")
    if d.month <= month_end:
        return "{}-{}".format(str(d.year-1), str(d.year)[2:4])
    else:
        return "{}-{}".format(str(d.year), str(d.year+1)[2:4])

def get_scaling_factor(value):
    if value > 2000000000:
        return (1000000000, '{:,.1f} billion', '{:,.1f}bn')
    elif value > 1500000:
        return (1000000, '{:,.1f} million', '{:,.1f}m')
    else:
        return (1, '{:,.0f}', '{:,.0f}')

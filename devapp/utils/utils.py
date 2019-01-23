
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

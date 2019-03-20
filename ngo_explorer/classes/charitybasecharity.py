from datetime import datetime

from ..utils.countries import get_country_by_id
from ..utils.charts import line_chart
from ..utils.inflation import fetch_inflation

class CharityBaseCharity(object):

    date_format = "%Y-%m-%d"

    def __init__(self, chardata):
        for k, v in chardata.items():
            setattr(self, k, v)

        self._set_name()
        self._get_countries()
        self._parse_website()
        self._parse_dates()
        self._get_inflation()

    def _get_inflation(self):
        self.inflation = fetch_inflation()

        self.current_year = str(datetime.now().year)
        if self.current_year not in self.inflation.keys():
            self.current_year = str(
                max([int(i) for i in self.inflation.keys()]))

        for f in self.finances:
            year = f["financialYear"]["end"].year
            inflator = self.inflation.get(
                self.current_year) / self.inflation.get(str(year))
            f["income_inflated"] = f["income"] * inflator
            f["spending_inflated"] = f["spending"] * inflator

    def _set_name(self):
        for n in self.names:
            if n["primary"]:
                self.name = n["value"]

    def _get_countries(self):
        areas = []
        countries = []
        if hasattr(self, "areas"):
            for a in self.areas:
                c = get_country_by_id(a["id"])
                if c:
                    countries.append(c)
                else:
                    areas.append(a)
        self.areas = areas
        self.countries = countries

    def _parse_website(self):
        if getattr(self, "website", None):
            self.website = self.website.strip()
            if not self.website.startswith("http"):
                self.website = "//" + self.website

    def _parse_dates(self):
        if getattr(self, "finances", None):
            # convert text strings to datetime
            for f in self.finances:
                if f.get("financialYear", {}).get("end"):
                    f["financialYear"]["end"] = datetime.strptime(
                        f["financialYear"]["end"][0:10], self.date_format)
                if f.get("financialYear", {}).get("start"):
                    f["financialYear"]["start"] = datetime.strptime(
                        f["financialYear"]["start"][0:10], self.date_format)

            # sort by financial year end
            self.finances = sorted(
                self.finances,
                key=lambda k: k["financialYear"]["end"],
                reverse=True,
            )

        if getattr(self, "registrations", None):
            # convert text strings to datetime
            for f in self.registrations:
                if f.get("registrationDate"):
                    f["registrationDate"] = datetime.strptime(
                        f["registrationDate"][0:10], self.date_format)
                if f.get("removalDate"):
                    f["removalDate"] = datetime.strptime(
                        f["removalDate"][0:10], self.date_format)

            # sort by date
            self.registrations = sorted(
                self.registrations,
                key=lambda k: k["registrationDate"]
            )

            self.registrationDate = self.registrations[0]["registrationDate"]
            self.removalDate = self.registrations[-1]["removalDate"]

    def finance_chart(self):
        if getattr(self, "finances", None):
            income_cash = [f.get("income") for f in self.finances]
            spending_cash = [f.get("spending") for f in self.finances]
            income_real = [f.get("income_inflated") for f in self.finances]
            spending_real = [f.get("spending_inflated") for f in self.finances]

            updatemenus = list([
                dict(
                    buttons=list([
                        dict(
                            args=[
                                {'y': [
                                    income_real,
                                    spending_real
                                ], "name": [
                                    "Income ({} prices)".format(self.current_year),
                                    "Spending ({} prices)".format(self.current_year),
                                ]}
                            ],
                            label='{} prices'.format(self.current_year),
                            method='restyle'
                        ),
                        dict(
                            args=[
                                {'y': [
                                    income_cash,
                                    spending_cash
                                ], "name": [
                                    "Income (cash terms)",
                                    "Spending (cash terms)",
                                ]}
                            ],
                            label='Cash terms',
                            method='restyle'
                        )
                    ]),
                    direction='down',
                    pad={'r': 0, 't': 10},
                    showactive=True,
                    type='buttons',
                    x=1.4,
                    xanchor='right',
                    y=0.9,
                    # yanchor='top',
                ),
            ])

            chart = line_chart([
                dict(
                    x=[f["financialYear"]["end"] for f in self.finances],
                    y=income_real,
                    name="Income ({} prices)".format(self.current_year),
                    mode="lines",
                    line=dict(
                        color="#0ca777",
                        width=4,
                    ),
                    hoverinfo='x+y',
                ),
                dict(
                    x=[f["financialYear"]["end"] for f in self.finances],
                    y=spending_real,
                    name="Spending ({} prices)".format(self.current_year),
                    mode="lines",
                    line=dict(
                        color="#F9AF42",
                        width=4,
                    ),
                    hoverinfo='x+y',
                )
            ])
            chart["layout"]["updatemenus"] = updatemenus
            return chart

    # def flat_dict(self):

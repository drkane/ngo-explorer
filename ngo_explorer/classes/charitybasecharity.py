from datetime import datetime

from flask_babel import _

from ..utils.charts import line_chart
from ..utils.countries import get_country_by_id
from ..utils.inflation import fetch_inflation
from ..utils.utils import nested_to_record


class CharityBaseCharity(object):

    date_format = "%Y-%m-%d"

    def __init__(self, chardata):
        for k, v in chardata.items():
            setattr(self, k, v)

        self._set_name()
        self._get_countries()
        self._parse_website()
        self._parse_dates()
        self._parse_orgids()
        self._parse_classifications()
        self._get_inflation()

    def _get_inflation(self):
        self._inflation = fetch_inflation()

        self._current_year = str(datetime.now().year)
        if self._current_year not in self._inflation.keys():
            self._current_year = str(max([int(i) for i in self._inflation.keys()]))

        for f in self.finances:
            if f.get("financialYear", {}).get("end") is None:
                continue
            year = f["financialYear"]["end"].year
            if self._inflation.get(str(year)):
                inflator = self._inflation.get(
                    self._current_year
                ) / self._inflation.get(str(year))
            else:
                inflator = 1

            if f.get("income"):
                f["income_inflated"] = f["income"] * inflator
            if f.get("spending"):
                f["spending_inflated"] = f["spending"] * inflator

    def _set_name(self):
        for n in self.names:
            if n["primary"]:
                self.name = n["value"]

    def _parse_orgids(self):
        if hasattr(self, "orgIds"):
            self.orgIds = [o["id"] for o in self.orgIds]

    def _parse_classifications(self):
        for i in ["operations", "beneficiaries", "causes"]:
            if hasattr(self, i):
                setattr(self, i, [o["id"] for o in getattr(self, i)])

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
            # remove any none attributes
            self.finances = [
                f
                for f in self.finances
                if (
                    f.get("income")
                    and f.get("spending")
                    and f.get("financialYear", {}).get("end")
                )
            ]

            # convert text strings to datetime
            for f in self.finances:
                if f.get("financialYear", {}).get("end"):
                    f["financialYear"]["end"] = datetime.strptime(
                        f["financialYear"]["end"][0:10], self.date_format
                    )
                if f.get("financialYear", {}).get("start"):
                    f["financialYear"]["start"] = datetime.strptime(
                        f["financialYear"]["start"][0:10], self.date_format
                    )

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
                        f["registrationDate"][0:10], self.date_format
                    )
                if f.get("removalDate"):
                    f["removalDate"] = datetime.strptime(
                        f["removalDate"][0:10], self.date_format
                    )

            # sort by date
            self.registrations = sorted(
                self.registrations, key=lambda k: k["registrationDate"]
            )

            self.registrationDate = self.registrations[0]["registrationDate"]
            self.removalDate = self.registrations[-1]["removalDate"]

    def finance_chart(self):
        if getattr(self, "finances", None):
            income_cash = [f.get("income") for f in self.finances]
            spending_cash = [f.get("spending") for f in self.finances]
            income_real = [f.get("income_inflated") for f in self.finances]
            spending_real = [f.get("spending_inflated") for f in self.finances]

            updatemenus = list(
                [
                    dict(
                        buttons=list(
                            [
                                dict(
                                    args=[
                                        {
                                            "y": [income_real, spending_real],
                                            "name": [
                                                _(
                                                    "Income (%(year)s prices)",
                                                    year=str(self._current_year),
                                                ),
                                                _(
                                                    "Spending (%(year)s prices)",
                                                    year=str(self._current_year),
                                                ),
                                            ],
                                        }
                                    ],
                                    label=_(
                                        "%(year)s prices", year=str(self._current_year)
                                    ),
                                    method="restyle",
                                ),
                                dict(
                                    args=[
                                        {
                                            "y": [income_cash, spending_cash],
                                            "name": [
                                                _("Income (cash terms)"),
                                                _("Spending (cash terms)"),
                                            ],
                                        }
                                    ],
                                    label=_("Cash terms"),
                                    method="restyle",
                                ),
                            ]
                        ),
                        direction="left",
                        pad={"r": 0, "t": 10},
                        showactive=True,
                        type="buttons",
                        x=0,
                        xanchor="left",
                        y=1.1,
                        yanchor="top",
                    ),
                ]
            )

            chart = line_chart(
                [
                    dict(
                        x=[f["financialYear"]["end"] for f in self.finances],
                        y=income_real,
                        name=_(
                            "Income (%(year)s prices)", year=str(self._current_year)
                        ),
                        mode="lines",
                        line=dict(
                            color="#0ca777",
                            width=4,
                        ),
                        hoverinfo="x+y",
                    ),
                    dict(
                        x=[f["financialYear"]["end"] for f in self.finances],
                        y=spending_real,
                        name=_(
                            "Spending (%(year)s prices)", year=str(self._current_year)
                        ),
                        mode="lines",
                        line=dict(
                            color="#F9AF42",
                            width=4,
                        ),
                        hoverinfo="x+y",
                    ),
                ]
            )
            chart["layout"]["updatemenus"] = updatemenus
            chart["layout"]["legend"] = dict(
                # x=0.5,
                # y=1,
                orientation="h"
            )
            return chart

    def as_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def as_flat_dict(self, inflation_adjusted=False):
        r = nested_to_record(self.as_dict())
        data = {}
        for k, v in r.items():

            if k == "finances":
                years_seen = []
                for f in v:
                    year = f["financialYear"]["end"].strftime("%Y")
                    if year in years_seen:
                        year = f["financialYear"]["end"].strftime("%Y%m%d")

                    if inflation_adjusted:
                        if "income" in f:
                            data[
                                "income_{}_{}prices".format(year, self._current_year)
                            ] = f.get("income_inflated")
                        if "spending" in f:
                            data[
                                "spending_{}_{}prices".format(year, self._current_year)
                            ] = f.get("spending_inflated")
                    else:
                        if "income" in f:
                            data["income_{}".format(year)] = f["income"]
                        if "spending" in f:
                            data["spending_{}".format(year)] = f["spending"]

                    years_seen.append(year)

            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    v = [i.get("name", list(i.values())[0]) for i in v]
                data[k] = ";".join(v)

            else:
                data[k] = v

        return data

from datetime import datetime

from ..utils.countries import get_country_by_id
from ..utils.charts import line_chart

class CharityBaseCharity(object):

    date_format = "%Y-%m-%d"

    def __init__(self, chardata):
        for k, v in chardata.items():
            setattr(self, k, v)

        self._set_name()
        self._get_countries()
        self._parse_website()
        self._parse_dates()

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
            return line_chart([{
                "x": [f["financialYear"]["end"] for f in self.finances],
                "y": [f.get("income") for f in self.finances],
                "name": "Income",
            }, {
                "x": [f["financialYear"]["end"] for f in self.finances],
                "y": [f.get("spending") for f in self.finances],
                "name": "Spending",
            }])

    # def flat_dict(self):

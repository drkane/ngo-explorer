import json
from dataclasses import InitVar, asdict, dataclass, field
from datetime import date, datetime
from typing import Optional

import plotly.graph_objs as go
from flask_babel import _

from ngo_explorer.classes.charts import ChartData
from ngo_explorer.classes.countries import Country
from ngo_explorer.classes.iati import OipaItemOrg
from ngo_explorer.utils.charts import line_chart
from ngo_explorer.utils.countries import get_country_by_id
from ngo_explorer.utils.utils import nested_to_record


@dataclass
class CharityName:
    value: str
    primary: bool = False


@dataclass
class CharityItem:
    id: str
    name: Optional[str] = None


@dataclass
class CharityFinancialYear:
    end: date
    start: Optional[date] = None

    def __post_init__(self):
        if isinstance(self.end, str):
            self.end = datetime.strptime(self.end, "%Y-%m-%d")
        if isinstance(self.start, str):
            self.start = datetime.strptime(self.start, "%Y-%m-%d")


@dataclass
class CharityFinance:
    financialYear: CharityFinancialYear
    income: Optional[float] = None
    spending: Optional[float] = None
    inflator: Optional[float] = None

    @property
    def income_inflated(self) -> Optional[float]:
        if isinstance(self.income, (int, float)) and isinstance(self.inflator, float):
            return float(self.income) * self.inflator

    @property
    def spending_inflated(self) -> Optional[float]:
        if isinstance(self.spending, (int, float)) and isinstance(self.inflator, float):
            return float(self.spending) * self.inflator

    @classmethod
    def from_db(cls, data: str):
        return cls(**json.loads(data))

    def __post_init__(self):
        if isinstance(self.financialYear, dict):
            self.financialYear = CharityFinancialYear(**self.financialYear)


@dataclass
class CharityGeoCodes:
    region: Optional[str] = None
    country: Optional[str] = None
    admin_county: Optional[str] = None
    admin_district: Optional[str] = None
    admin_ward: Optional[str] = None
    parliamentary_constituency: Optional[str] = None
    lsoa: Optional[str] = None
    msoa: Optional[str] = None


@dataclass
class CharityGeo:
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region: Optional[str] = None
    country: Optional[str] = None
    admin_county: Optional[str] = None
    admin_district: Optional[str] = None
    admin_ward: Optional[str] = None
    lsoa: Optional[str] = None
    msoa: Optional[str] = None
    parliamentary_constituency: Optional[str] = None
    codes: Optional[CharityGeoCodes] = None

    @classmethod
    def from_db(cls, data: Optional[str] = None):
        if not data:
            return cls()
        data_dict = json.loads(data)
        if data_dict.get("codes"):
            data_dict["codes"] = CharityGeoCodes(**data_dict["codes"])
        return cls(**data_dict)


@dataclass
class CharityRegistration:
    registrationDate: Optional[date] = None
    removalDate: Optional[date] = None

    def __post_init__(self):
        if isinstance(self.registrationDate, str):
            self.registrationDate = datetime.strptime(self.registrationDate, "%Y-%m-%d")
        if isinstance(self.removalDate, str):
            self.removalDate = datetime.strptime(self.removalDate, "%Y-%m-%d")


@dataclass
class CharityContacts:
    email: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    postcode: Optional[str] = None


@dataclass
class CharityNumPeople:
    trustees: int
    volunteers: int
    employees: int


@dataclass
class Charity:
    id: Optional[str] = None
    name: Optional[str] = None
    names: Optional[list[CharityName]] = None
    activities: Optional[str] = None
    areas: Optional[list[CharityItem]] = None
    finances: Optional[list[CharityFinance]] = None
    orgIds: Optional[list[str]] = None
    operations: Optional[list[str]] = None
    causes: Optional[list[str]] = None
    beneficiaries: Optional[list[str]] = None
    geo: Optional[CharityGeo] = None
    registrations: Optional[list[CharityRegistration]] = None
    website: Optional[str] = None
    contact: Optional[CharityContacts] = None
    numPeople: Optional[CharityNumPeople] = None
    governingDoc: Optional[str] = None
    areaOfBenefit: Optional[str] = None
    countries: Optional[list[Country]] = None
    iati: Optional[list[OipaItemOrg]] = None

    current_year: str = field(init=False)
    inflation: InitVar[Optional[dict[str, float]]] = None

    @classmethod
    def from_db(
        cls,
        data: dict[str, str],
        all_finances: bool = False,
        inflation: Optional[dict[str, float]] = None,
    ):
        if all_finances:
            charity_finances = data.get("all_finances", "[]")
        else:
            charity_finances = data.get("finances", "[]")

        countries_list: list[str] = json.loads(data.get("countries", "[]"))
        countries = []
        for country in countries_list:
            country_obj = get_country_by_id(country)
            if country_obj:
                countries.append(country_obj)

        all_names = []
        if data.get("all_names"):
            all_names = json.loads(data.get("all_names", "[]"))

        return cls(
            id=data.get("id"),
            name=data.get("name"),
            names=[CharityName(**n) for n in all_names],
            activities=data.get("activities"),
            areas=[CharityItem(**a) for a in json.loads(data.get("areas", "[]"))],
            finances=[CharityFinance(**f) for f in json.loads(charity_finances)],
            orgIds=[o["id"] for o in json.loads(data.get("orgids", "[]"))],
            operations=[o["id"] for o in json.loads(data.get("operations", "[]"))],
            causes=[o["id"] for o in json.loads(data.get("causes", "[]"))],
            beneficiaries=[
                o["id"] for o in json.loads(data.get("beneficiaries", "[]"))
            ],
            geo=CharityGeo.from_db(data.get("geo", "{}")),
            registrations=[
                CharityRegistration(**r)
                for r in json.loads(data.get("registrations", "[]"))
            ],
            website=data.get("website"),
            contact=CharityContacts(
                **json.loads(data.get("contact", data.get("contacts", "{}")))
            ),
            numPeople=CharityNumPeople(**json.loads(data.get("numPeople", "{}"))),
            governingDoc=data.get("governingDoc"),
            areaOfBenefit=data.get("areaOfBenefit"),
            countries=countries,
            inflation=inflation,
        )

    def __post_init__(self, inflation: Optional[dict[str, float]] = None):
        # sort by financial year end
        if self.finances:
            self.finances = sorted(
                self.finances,
                key=lambda k: k.financialYear.end,
                reverse=True,
            )

        self.current_year = str(datetime.now().year)

        self._parse_website()
        self._get_inflation(inflation)

    def _get_inflation(self, inflation: Optional[dict[str, float]] = None):
        if inflation and self.current_year not in inflation.keys():
            self.current_year = str(max([int(i) for i in inflation.keys()]))

        if self.finances and inflation:
            current_year_inflation = inflation.get(self.current_year)
            for f in self.finances:
                if f.financialYear.end is None:
                    continue
                year = f.financialYear.end.year
                year_inflation = inflation.get(str(year))
                if year_inflation and current_year_inflation:
                    f.inflator = current_year_inflation / year_inflation
                else:
                    f.inflator = 1

    def _parse_website(self):
        if self.website:
            self.website = self.website.strip()
            if not self.website.startswith("http"):
                self.website = "https://" + self.website

    @property
    def registrationDate(self):
        if self.registrations:
            return self.registrations[0].registrationDate

    @property
    def removalDate(self):
        if self.registrations:
            return self.registrations[0].removalDate

    def finance_chart(self):
        if self.finances:
            income_cash = [getattr(f, "income") for f in self.finances]
            spending_cash = [getattr(f, "spending") for f in self.finances]
            income_real = [getattr(f, "income_inflated") for f in self.finances]
            spending_real = [getattr(f, "spending_inflated") for f in self.finances]

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
                                                    year=str(self.current_year),
                                                ),
                                                _(
                                                    "Spending (%(year)s prices)",
                                                    year=str(self.current_year),
                                                ),
                                            ],
                                        }
                                    ],
                                    label=_(
                                        "%(year)s prices", year=str(self.current_year)
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

            chart: ChartData = line_chart(
                [
                    go.Scatter(
                        x=[f.financialYear.end for f in self.finances],
                        y=income_real,
                        name=_("Income (%(year)s prices)", year=str(self.current_year)),
                        mode="lines",
                        line=dict(
                            color="#0ca777",
                            width=4,
                        ),
                        hoverinfo="x+y",
                    ),
                    go.Scatter(
                        x=[f.financialYear.end for f in self.finances],
                        y=spending_real,
                        name=_(
                            "Spending (%(year)s prices)", year=str(self.current_year)
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
            if v and isinstance(v, list) and isinstance(v[0], (CharityRegistration)):
                v = v[0]

            if (
                k == "finances"
                and isinstance(v, list)
                and isinstance(v[0], (CharityFinance))
            ):
                for f in v:
                    if not f.financialYear.end:
                        continue
                    year = f.financialYear.end.year

                    income_val = None
                    spending_val = None
                    if inflation_adjusted:
                        if f.income is not None:
                            income_col = "income_{}_{}prices".format(
                                year, self.current_year
                            )
                            income_val = f.income_inflated
                        if f.spending is not None:
                            spending_col = "spending_{}_{}prices".format(
                                year, self.current_year
                            )
                            spending_val = f.spending_inflated
                    else:
                        if f.income is not None:
                            income_col = "income_{}".format(year)
                            income_val = f.income
                        if f.spending is not None:
                            spending_col = "spending_{}".format(year)
                            spending_val = f.spending

                    if income_val:
                        if income_col not in data:
                            data[income_col] = 0
                        data[income_col] += income_val
                    if spending_val:
                        if spending_col not in data:
                            data[spending_col] = 0
                        data[spending_col] += spending_val

            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    v = [i.get("name", list(i.values())[0]) for i in v]
                elif v and isinstance(v[0], (CharityItem, Country)):
                    v = [i.name for i in v]
                data[k] = ";".join([str(item) for item in v])

            elif isinstance(
                v, (CharityContacts, CharityGeo, CharityRegistration, CharityNumPeople)
            ):
                for k2, v2 in nested_to_record(asdict(v), prefix=k).items():
                    data[k2] = v2

            else:
                data[k] = v

        return data

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Country:
    id: str  #  "D-1",
    name: str  #  "Afghanistan",
    continent: str  #  "Asia",
    iso: str  #  "AFG",
    iso2: str  #  "AF",
    latitude: float  #  33.93911,
    longitude: float  #  67.709953
    ngoaidmap: Optional[str] = None  #  "gn_1149361",
    dac_status: Optional[str] = None  #  "Least developed",
    undp: Optional[str] = None  #  "South Asia",
    filtered: Optional[bool] = None  #  False
    count: Optional[int] = None


@dataclass
class CountryGroupValue:
    id: str
    name: str


@dataclass
class CountryGroup:
    values: list[CountryGroupValue]
    show_initial: bool
    title: Optional[str] = None


@dataclass
class CountryGroupItem:
    name: str
    countries: list[Country]


@dataclass
class CountryGroupItemUpload:
    name: str
    countries: list[Country] = field(default_factory=list)
    type_: str = "upload"


@dataclass
class CountryGroupItemList:
    names: list[str]
    countries: list[Country]

    @property
    def name(self):
        return ", ".join(self.names)


@dataclass
class Initiative:
    homepage: str  #  "https://pfongue.org/",
    title: str  #  _("Platform of European NGOs in Senegal"),
    directlink: Optional[str] = None  #  "https://pfongue.org/-Cartographie-.html",
    directlinktext: Optional[str] = None  #  _("Map of projects"),
    source: Optional[str] = None  #  "Forus"
    source_link: Optional[str] = (
        None  #  "http://forus-international.org/en/about-us/who-we-are"
    )

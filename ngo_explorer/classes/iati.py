from dataclasses import dataclass
from typing import Optional, TypedDict

from ngo_explorer.classes.countries import Country


class OipaItem(TypedDict):
    ref: str
    name: str
    count: int


@dataclass
class OipaItemOrg:
    ref: str
    name: str
    count: int
    country: Optional[Country] = None

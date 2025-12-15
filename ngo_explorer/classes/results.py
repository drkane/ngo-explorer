from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResultBucket:
    key: str
    count: int
    name: Optional[str] = None
    sum: Optional[int] = None
    sumIncomeText: Optional[str] = None


@dataclass
class ResultAggregateFinances:
    latestSpending: list[ResultBucket] = field(default_factory=list)


@dataclass
class ResultAggregateGeo:
    region: list[ResultBucket] = field(default_factory=list)
    country: list[ResultBucket] = field(default_factory=list)


@dataclass
class ResultAggregate:
    finances: ResultAggregateFinances = field(default_factory=ResultAggregateFinances)
    causes: list[ResultBucket] = field(default_factory=list)
    beneficiaries: list[ResultBucket] = field(default_factory=list)
    operations: list[ResultBucket] = field(default_factory=list)
    areas: list[ResultBucket] = field(default_factory=list)
    countries: list[ResultBucket] = field(default_factory=list)
    geo: ResultAggregateGeo = field(default_factory=ResultAggregateGeo)

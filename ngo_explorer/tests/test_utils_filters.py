import pytest

from ngo_explorer.utils.filters import parse_filters

def test_parse_filters():
    # default is to return max_countries
    assert "max_countries" in parse_filters({})

    # if filter not recognised then it's not included
    assert len(parse_filters({"made-up-filter": "blahblah"}))==1

    # filter for int values
    assert parse_filters({"filter-max-countries": "60"})["max_countries"] == 60
    assert parse_filters({"filter-max-income": "60000"})["max_income"] == 60000
    assert parse_filters({"filter-min-income": "60000"})["min_income"] == 60000

    # filter for search
    assert "search" not in parse_filters({"filter-search": ""})
    assert parse_filters({"filter-search": "test"})["search"] == '"test"'
    assert parse_filters({"filter-search": "test OR test2"})["search"] == 'test OR test2'
    assert parse_filters({"filter-search": 'test "test2"'})["search"] == 'test "test2"'

    # flags
    assert parse_filters({"filter-exclude-grantmakers": "test"})["exclude_grantmakers"] == True
    assert parse_filters({"filter-exclude-religious": "test"})["exclude_religious"] == True
    assert parse_filters({"filter-exclude-grantmakers": ""})["exclude_grantmakers"] == True
    assert parse_filters({"filter-exclude-religious": ""}
                         )["exclude_religious"] == True

    # @TODO: test classification and country lists
    # need to import multidict
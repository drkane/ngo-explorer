from werkzeug.datastructures import MultiDict

from ngo_explorer.utils.filters import parse_filters


def test_parse_filters():
    # default is to return max_countries
    assert getattr(parse_filters(MultiDict({})), "max_countries")

    # if filter not recognised then it's not included
    # assert len(parse_filters(MultiDict({"made-up-filter": "blahblah"})) == 1

    # filter for int values
    assert parse_filters(MultiDict({"filter-max-countries": "60"})).max_countries == 60
    assert parse_filters(MultiDict({"filter-max-income": "60000"})).max_income == 60000
    assert parse_filters(MultiDict({"filter-min-income": "60000"})).min_income == 60000

    # filter for search
    assert parse_filters(MultiDict({"filter-search": ""})).search is None
    assert parse_filters(MultiDict({"filter-search": "test"})).search == '"test"'
    assert (
        parse_filters(MultiDict({"filter-search": "test OR test2"})).search
        == "test OR test2"
    )
    assert (
        parse_filters(MultiDict({"filter-search": 'test "test2"'})).search
        == 'test "test2"'
    )

    # flags
    assert parse_filters(
        MultiDict({"filter-exclude-grantmakers": "test"})
    ).exclude_grantmakers
    assert parse_filters(
        MultiDict({"filter-exclude-religious": "test"})
    ).exclude_religious
    assert parse_filters(
        MultiDict({"filter-exclude-grantmakers": ""})
    ).exclude_grantmakers
    assert parse_filters(MultiDict({"filter-exclude-religious": ""})).exclude_religious

    # @TODO: test classification and country lists
    # need to import multidict

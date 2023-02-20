import pytest

from ngo_explorer.utils.utils import (
    correct_titlecase,
    get_scaling_factor,
    nested_to_record,
    record_to_nested,
    scale_value,
    update_url_values,
)


def test_scaling_factor():
    with pytest.raises(TypeError):
        assert get_scaling_factor("kljsdg")
    assert get_scaling_factor(-200) == (1, "{:,.0f}", "{:,.0f}")
    assert get_scaling_factor(0) == (1, "{:,.0f}", "{:,.0f}")
    assert get_scaling_factor(1) == (1, "{:,.0f}", "{:,.0f}")
    assert get_scaling_factor(10) == (1, "{:,.0f}", "{:,.0f}")
    assert get_scaling_factor(1000) == (1, "{:,.0f}", "{:,.0f}")
    assert get_scaling_factor(1000.9353) == (1, "{:,.0f}", "{:,.0f}")
    assert get_scaling_factor(1500000) == (1, "{:,.0f}", "{:,.0f}")
    assert get_scaling_factor(2000000) == (1000000, "{:,.1f} million", "{:,.1f}m")
    assert get_scaling_factor(2000000.353) == (1000000, "{:,.1f} million", "{:,.1f}m")
    assert get_scaling_factor(2000000000) == (1000000, "{:,.1f} million", "{:,.1f}m")
    assert get_scaling_factor(3000000000) == (
        1000000000,
        "{:,.1f} billion",
        "{:,.1f}bn",
    )
    assert get_scaling_factor(float("inf")) == (
        1000000000,
        "{:,.1f} billion",
        "{:,.1f}bn",
    )


def test_scale_value():
    with pytest.raises(TypeError):
        scale_value("kljsdg")
    assert scale_value(-200) == "-200"
    assert scale_value(0) == "0"
    assert scale_value(1) == "1"
    assert scale_value(10) == "10"
    assert scale_value(1000) == "1,000"
    assert scale_value(1000.9353) == "1,001"
    assert scale_value(1500000) == "1,500,000"
    assert scale_value(2000000) == "2.0 million"
    assert scale_value(2000000.353) == "2.0 million"
    assert scale_value(2000000000) == "2,000.0 million"
    assert scale_value(3000000000) == "3.0 billion"
    assert scale_value(float("inf")) == "inf billion"
    assert scale_value(1500000, True) == "1,500,000"
    assert scale_value(2000000, True) == "2.0m"
    assert scale_value(2000000.353, True) == "2.0m"
    assert scale_value(2000000000, True) == "2,000.0m"
    assert scale_value(3000000000, True) == "3.0bn"
    assert scale_value(float("inf"), True) == "infbn"


def test_update_url_values():
    test_url = "http://example.com/"
    with pytest.raises(TypeError):
        update_url_values(test_url, None) == test_url
        update_url_values(test_url, "hithere") == test_url
    assert update_url_values(test_url, {}) == test_url
    assert update_url_values(test_url, {"test": "test"}) == test_url + "?test=test"
    assert (
        update_url_values(test_url + "?test=abcd", {"test": "test"})
        == test_url + "?test=test"
    )
    assert (
        update_url_values(test_url, {"test": ["test1", "test2"]})
        == test_url + "?test=test1&test=test2"
    )
    assert (
        update_url_values(
            test_url + "?test=abcd", {"test": ["test1", "test2"], "testB": "testBvalue"}
        )
        == test_url + "?test=test1&test=test2&testB=testBvalue"
    )


def test_record_to_nested():
    fields = [
        "singlefield",
        "multiple.joined.up.fields",
        "anothersinglefield",
        "combine.field1",
        "combine.field2",
    ]
    result = record_to_nested(fields)
    assert isinstance(result["singlefield"], dict)
    assert len(result["singlefield"]) == 0

    assert isinstance(result["anothersinglefield"], dict)
    assert len(result["anothersinglefield"]) == 0

    assert isinstance(result["multiple"], dict)
    assert len(result["multiple"]) == 1
    assert isinstance(result["multiple"]["joined"], dict)
    assert len(result["multiple"]["joined"]) == 1
    assert isinstance(result["multiple"]["joined"]["up"], dict)
    assert len(result["multiple"]["joined"]["up"]) == 1
    assert isinstance(result["multiple"]["joined"]["up"]["fields"], dict)
    assert len(result["multiple"]["joined"]["up"]["fields"]) == 0

    assert isinstance(result["combine"], dict)
    assert len(result["combine"]) == 2
    assert isinstance(result["combine"]["field1"], dict)
    assert len(result["combine"]["field1"]) == 0
    assert isinstance(result["combine"]["field2"], dict)
    assert len(result["combine"]["field2"]) == 0

    with pytest.raises(AttributeError):
        record_to_nested([1234])


def test_nested_to_record():
    fields = {
        "singlefield": 12,
        "multiple": {"joined": {"up": {"fields": "result"}}},
        "anothersinglefield": None,
        "combine": {
            "field1": "12",
            "field2": "cd",
        },
    }
    result = nested_to_record(fields)

    assert "multiple.joined.up.fields" in result
    assert result["combine.field2"] == "cd"
    assert result["anothersinglefield"] == None

    fields_with_list = {
        "listfield": [
            "listitem1",
            "listitem2",
        ]
    }
    result = nested_to_record(fields_with_list)

    assert isinstance(result["listfield"], list)


def test_correct_titlecase():
    names = [
        "The St. Endellion Festivals Trust",
        "Friends of North Heath CP School",
        "A M Challis Trust Ltd",
        "Majlis Al-Falah Trust (UK)",
        "Kilby Woodland Trust Ltd",
        "Biocentre UK",
        "Bury St.Edmunds Methodist Circuit",
        "Ridgeway School PTA",
        "St Matthews High Brooms PFA",
        "Friends of the Gwyn Hall, Neath",
        "1st Shifnal Scout Group",
        "SV2G (St Vincent & the Grenadines, 2nd Generation",
        "103rd Reading (Oxford Road) Scout Group",
        "The 4th London Collection",
        "Dr Smith's Charity",
        "The PDC Trust",
        "35th Norwich Sea Scouts",
        "Adept - Yorkshire ADHD and Learning Ability Support Group",
        "Tuesday O'Hara Fund",
        "Ysgol Cwm-Y-Glo School P.T.A.",
        "Clwb Llawen Y Llys",
        "Activities 4 Children (Sheffield)Limited",
        "Prince Albert II of Monaco Foundation (GB)",
        "The Drs Hady Bayoumi & Rashida Mangera Charitable Trust",
        "KT's Fund",
        "St Michaels CE (VC) Combined School Fund",
    ]

    for n in names:
        assert n == correct_titlecase(n)

    assert "the PDC Trust" == correct_titlecase("The PDC Trust", False)
    assert "Tuesday O'Hara Fund" == correct_titlecase("Tuesday O'Hara Fund", False)

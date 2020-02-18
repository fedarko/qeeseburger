import pytest
import pandas as pd
from ..add_host_ages import _add_host_ages


# TODO: test badly formatted dates in the dataset; test impossible birthdays
# (sample date before birthday); etc.
# TODO: test float years stuff with:
#  -extra precision (e.g. hour/minute stuff) -- should be ignored, both if on
#   birthday and if on sample timestamp


def get_test_data():
    host_ids = "ABC,DEF"
    host_bdays = "2000-05-06, 1993-02-18"
    md = pd.DataFrame(
        {
            "host_subject_id": ["ABC", "DEF", "ABC", "ABC", "DEF", "GHI"],
            "collection_timestamp": [
                "1/3/14",  # ABC
                "1/4/2014",  # DEF
                "2014-01-05",  # ABC
                "2015-01-14",  # ABC
                "1995-07-21",  # DEF
                "1996-12-15",  # GHI
            ],
        },
        index=["S1", "S2", "S3", "S4", "S5", "S6"],
    )
    return md, host_ids, host_bdays


def test_good():
    new_md = _add_host_ages(*get_test_data())
    assert new_md.at["S1", "host_age_years"] == "13"
    assert new_md.at["S2", "host_age_years"] == "20"
    assert new_md.at["S3", "host_age_years"] == "13"
    assert new_md.at["S4", "host_age_years"] == "14"
    assert new_md.at["S5", "host_age_years"] == "2"
    assert new_md.at["S6", "host_age_years"] == "not applicable"


def test_no_ids_or_bdays_given():
    with pytest.raises(ValueError) as einfo:
        _add_host_ages(get_test_data()[0], "", "")
    assert "No host IDs and/or birthdays were specified." in str(einfo.value)


def test_mismatched_ids_and_bdays():
    data = get_test_data()
    with pytest.raises(ValueError) as einfo:
        _add_host_ages(data[0], data[1], "1999-01-25")
    assert "Number of host IDs doesn't match" in str(einfo.value)


def test_redundant_ids():
    data = get_test_data()
    with pytest.raises(ValueError) as einfo:
        _add_host_ages(data[0], "ABC,ABC", data[2])
    assert "specified host IDs aren't unique" in str(einfo.value)


def test_badly_formatted_bdays():
    data = get_test_data()
    with pytest.raises(ValueError) as einfo:
        _add_host_ages(data[0], data[1], "blasdfoj,lol i'm incorrect")
    assert "birthdays aren't correctly formatted." in str(einfo.value)


def test_float_years():
    md = pd.DataFrame(
        {"host_subject_id": ["ABC"], "collection_timestamp": ["1995-11-20"]},
        index=["S1"],
    )
    new_md = _add_host_ages(md, "ABC", "1990-12-01", float_years=True)
    assert new_md.at["S1", "host_age"] == "4.9693"

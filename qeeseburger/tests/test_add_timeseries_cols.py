import pytest
import pandas as pd
from ..add_timeseries_cols import _add_extra_cols


def get_test_data():
    m_df = pd.DataFrame(
        {
            "host_subject_id": ["ABC", "DEF", "ABC", "ABC"],
            "collection_timestamp": [
                "January 3, 2014",
                "January 4, 2014",
                "2014-01-05",
                "2015-01-14",
            ],
        },
        index=["S1", "S2", "S3", "S4"],
    )
    return "ABC", "1984-01-01", m_df


def test_good():
    new_metadata_df = _add_extra_cols(*(get_test_data()))

    # All of these timestamps are valid
    assert new_metadata_df["is_collection_timestamp_valid"].all()

    # Check host_age_years values
    assert new_metadata_df.loc["S1", "host_age_years"] == "30"
    # This value is "not applicable" since S2's host_subject_id is DEF, not ABC
    assert new_metadata_df.loc["S2", "host_age_years"] == "not applicable"
    assert new_metadata_df.loc["S3", "host_age_years"] == "30"
    assert new_metadata_df.loc["S4", "host_age_years"] == "31"

    # Check ordinal_timestamp values
    assert new_metadata_df.loc["S1", "ordinal_timestamp"] == "20140103"
    assert new_metadata_df.loc["S2", "ordinal_timestamp"] == "20140104"
    assert new_metadata_df.loc["S3", "ordinal_timestamp"] == "20140105"
    assert new_metadata_df.loc["S4", "ordinal_timestamp"] == "20150114"

    # Check days_since_first_day values
    # Note that these are independent of the host_subject_id -- the "first day"
    # is computed considering all valid collection_timestamp values
    assert new_metadata_df.loc["S1", "days_since_first_day"] == "0"
    assert new_metadata_df.loc["S2", "days_since_first_day"] == "1"
    assert new_metadata_df.loc["S3", "days_since_first_day"] == "2"
    # "Ground truth" value computed using
    # https://www.timeanddate.com/date/durationresult.html?m1=1&d1=3&y1=2014&m2=1&d2=14&y2=2015
    assert new_metadata_df.loc["S4", "days_since_first_day"] == "376"


def test_that_lack_of_required_cols_triggers_error():
    cols_to_drop = [
        ["host_subject_id"],
        ["collection_timestamp"],
        ["collection_timestamp", "host_subject_id"],
    ]
    for c in cols_to_drop:
        host_subject_id, host_birthday, m_df = get_test_data()
        m_df.drop(c, axis="columns", inplace=True)
        with pytest.raises(ValueError) as einfo:
            _add_extra_cols(host_subject_id, host_birthday, m_df)
        assert "must include the following columns" in str(einfo.value)


def test_impossible_birthday():
    host_subject_id, host_birthday, m_df = get_test_data()
    host_birthday = "March 10, 2014"
    with pytest.raises(ValueError) as einfo:
        _add_extra_cols(host_subject_id, host_birthday, m_df)
    # S1 is expected to come up in the error message because it's the first in
    # the index
    assert (
        "Sample S1 has a collection_timestamp, January 3, 2014, occurring "
        "before the host birthday of March 10, 2014."
    ) in str(einfo.value)


def test_birthday_on_sampling_day():
    host_subject_id, host_birthday, m_df = get_test_data()
    # This should work -- the host will just have a host_age_years value of 0
    host_birthday = "January 3, 2014"
    new_m_df = _add_extra_cols(host_subject_id, host_birthday, m_df)
    assert new_m_df.loc["S1", "host_age_years"] == "0"
    assert new_m_df.loc["S2", "host_age_years"] == "not applicable"
    assert new_m_df.loc["S3", "host_age_years"] == "0"
    assert new_m_df.loc["S4", "host_age_years"] == "1"


def test_invalid_timestamp():
    """Tests that samples with invalid timestamps are handled properly."""

    host_subject_id, host_birthday, m_df = get_test_data()
    m_df.loc["S3", "collection_timestamp"] = "asodifjoaisdjf"
    new_m_df = _add_extra_cols(host_subject_id, host_birthday, m_df)

    assert new_m_df.loc["S1", "is_collection_timestamp_valid"] == "True"
    assert new_m_df.loc["S2", "is_collection_timestamp_valid"] == "True"
    assert new_m_df.loc["S3", "is_collection_timestamp_valid"] == "False"
    assert new_m_df.loc["S4", "is_collection_timestamp_valid"] == "True"

    assert new_m_df.loc["S1", "host_age_years"] == "30"
    assert new_m_df.loc["S2", "host_age_years"] == "not applicable"
    assert new_m_df.loc["S3", "host_age_years"] == "not applicable"
    assert new_m_df.loc["S4", "host_age_years"] == "31"

    assert new_m_df.loc["S1", "ordinal_timestamp"] == "20140103"
    assert new_m_df.loc["S2", "ordinal_timestamp"] == "20140104"
    assert new_m_df.loc["S3", "ordinal_timestamp"] == "not applicable"
    assert new_m_df.loc["S4", "ordinal_timestamp"] == "20150114"

    assert new_m_df.loc["S1", "days_since_first_day"] == "0"
    assert new_m_df.loc["S2", "days_since_first_day"] == "1"
    assert new_m_df.loc["S3", "days_since_first_day"] == "not applicable"
    assert new_m_df.loc["S4", "days_since_first_day"] == "376"

import pytest
import pandas as pd
from ..add_timeseries_cols import _add_extra_cols


def get_test_data():
    return pd.DataFrame(
        {
            "host_subject_id": ["ABC", "DEF", "ABC", "ABC"],
            "collection_timestamp": [
                "1/3/14",
                "1/4/2014",
                "2014-01-05",
                "2015-01-14",
            ],
        },
        index=["S1", "S2", "S3", "S4"],
    )


def test_good():
    new_metadata_df = _add_extra_cols(get_test_data())

    # All of these timestamps are valid
    assert new_metadata_df["is_collection_timestamp_valid"].all()

    # Check ordinal_timestamp values
    assert new_metadata_df.loc["S1", "ordinal_timestamp"] == "20140103"
    assert new_metadata_df.loc["S2", "ordinal_timestamp"] == "20140104"
    assert new_metadata_df.loc["S3", "ordinal_timestamp"] == "20140105"
    assert new_metadata_df.loc["S4", "ordinal_timestamp"] == "20150114"

    # Check days_since_first_day values
    # Note that these are independent of any host_subject_id -- the "first day"
    # is computed considering all valid collection_timestamp values
    assert new_metadata_df.loc["S1", "days_since_first_day"] == "0"
    assert new_metadata_df.loc["S2", "days_since_first_day"] == "1"
    assert new_metadata_df.loc["S3", "days_since_first_day"] == "2"
    # "Ground truth" value computed using
    # https://www.timeanddate.com/date/durationresult.html?m1=1&d1=3&y1=2014&m2=1&d2=14&y2=2015
    assert new_metadata_df.loc["S4", "days_since_first_day"] == "376"


def test_lack_of_required_cols():
    m_df = get_test_data()
    m_df.drop(["collection_timestamp"], axis="columns", inplace=True)
    with pytest.raises(ValueError) as einfo:
        _add_extra_cols(m_df)
    assert "must include the following columns" in str(einfo.value)


def test_invalid_timestamp():
    """Tests that samples with invalid timestamps are handled properly."""

    m_df = get_test_data()
    m_df.loc["S3", "collection_timestamp"] = "asodifjoaisdjf"
    new_m_df = _add_extra_cols(m_df)

    assert new_m_df.loc["S1", "is_collection_timestamp_valid"] == "True"
    assert new_m_df.loc["S2", "is_collection_timestamp_valid"] == "True"
    assert new_m_df.loc["S3", "is_collection_timestamp_valid"] == "False"
    assert new_m_df.loc["S4", "is_collection_timestamp_valid"] == "True"

    assert new_m_df.loc["S1", "ordinal_timestamp"] == "20140103"
    assert new_m_df.loc["S2", "ordinal_timestamp"] == "20140104"
    assert new_m_df.loc["S3", "ordinal_timestamp"] == "not applicable"
    assert new_m_df.loc["S4", "ordinal_timestamp"] == "20150114"

    assert new_m_df.loc["S1", "days_since_first_day"] == "0"
    assert new_m_df.loc["S2", "days_since_first_day"] == "1"
    assert new_m_df.loc["S3", "days_since_first_day"] == "not applicable"
    assert new_m_df.loc["S4", "days_since_first_day"] == "376"


def test_output_cols_in_input():
    output_cols = {
        "ordinal_timestamp",
        "days_since_first_day",
        "is_collection_timestamp_valid",
    }
    for c in output_cols:
        m_df = get_test_data()
        m_df[c] = "blahblahblah"
        with pytest.raises(ValueError) as einfo:
            _add_extra_cols(m_df)
        assert (
            "already includes at least one of the following columns"
        ) in str(einfo.value)

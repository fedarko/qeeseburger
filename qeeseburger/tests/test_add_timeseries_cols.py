import pandas as pd
from dateutil.parser import parse
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
    assert new_metadata_df["is_collection_timestamp_valid"].all()
    # TODO test other cols...

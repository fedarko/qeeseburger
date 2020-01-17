#! /usr/bin/env python3
import click
from arrow import ParserError
from .utils import (
    strict_parse,
    check_cols_present,
    check_cols_not_present,
    manipulate_md,
)


def _add_extra_cols(metadata_df):
    """Returns a DataFrame modified as expected."""

    m_df = metadata_df.copy()
    check_cols_present(m_df, {"collection_timestamp"})
    check_cols_not_present(
        m_df,
        {
            "ordinal_timestamp",
            "days_since_first_day",
            "is_collection_timestamp_valid",
        },
    )

    # only call strict_parse() on sample timestamps once
    sampleid2date = {}

    def get_time_validity_and_parse_date(row):
        try:
            # we convert the timestamp to a string just in case it's something
            # funky like a float
            # (non-str timestamps could ostensibly be valid, for example if
            # they're all formatted like 20200109. that being said, doing this
            # conversion here makes me feel dirty so if you're reading this i
            # still recommend that timestamps be specified as strings from the
            # get-go.)
            date = strict_parse(str(row["collection_timestamp"]))
            sampleid2date[row.name] = date
            # If strict_parse() didn't fail, the timestamp should be valid
            return "True"
        except ParserError:
            return "False"

    # 1. Add on is_collection_timestamp_valid column
    # Use of apply() over a basic loop based on
    # https://engineering.upside.com/a-beginners-guide-to-optimizing-pandas-code-for-speed-c09ef2c6a4d6
    m_df["is_collection_timestamp_valid"] = m_df.apply(
        get_time_validity_and_parse_date, axis=1
    )

    # 2. Add ordinal timestamp for all samples

    def get_ordinal_timestamp(row):
        if row["is_collection_timestamp_valid"] == "True":
            return sampleid2date[row.name].isoformat().replace("-", "")
        else:
            return "not applicable"

    m_df["ordinal_timestamp"] = m_df.apply(get_ordinal_timestamp, axis=1)

    # 3. Add days elapsed

    # 3.1. Compute earliest date
    min_date = min(sampleid2date.values())

    print("Earliest date is {}.".format(min_date))

    # 3.2. Assign "days from first timestamp" metric for each sample
    # (the sample(s) taken on min_date should have a value of 0, and samples
    # taken on the next day day later would have a value of 1, ...)
    # There is some inherent imprecision here due to different levels of
    # precision in sample collection (e.g. down to the day vs. down to the
    # minute), but this should be sufficient for exploratory visualization.

    def get_days_since(row):
        if row["is_collection_timestamp_valid"] == "True":
            # Note the avoidance of relativedelta -- see
            # https://stackoverflow.com/a/48262147/10730311
            return str((sampleid2date[row.name] - min_date).days)
        else:
            return "not applicable"

    m_df["days_since_first_day"] = m_df.apply(get_days_since, axis=1)

    return m_df


@click.command()
@click.option(
    "-i",
    "--input-metadata-file",
    required=True,
    help=(
        "Input metadata filepath. Must contain a collection_timestamp column."
    ),
    type=str,
)
@click.option(
    "-o",
    "--output-metadata-file",
    required=True,
    help="Output metadata filepath. Will contain some additional columns.",
    type=str,
)
def add_columns(input_metadata_file, output_metadata_file) -> None:
    """Add some useful columns for time-series studies to a metadata file.

    In particular, the columns added are "is_collection_timestamp_valid",
    "ordinal_timestamp", and "days_since_first_day".

    Note that the value of days_since_first_day may vary even between samples
    with identical collection_timestamp values if you run this script on
    different metadata files. This is because the "first day" is computed
    relative to all of the valid collection_timestamps in the input metadata
    file; to ensure that the values in this column are comparable between
    datasets, you should merge metadata and then run this script.
    """
    manipulate_md(
        input_metadata_file, [], output_metadata_file, _add_extra_cols
    )


if __name__ == "__main__":
    add_columns()

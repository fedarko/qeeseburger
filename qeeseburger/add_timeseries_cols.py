#! /usr/bin/env python3
import click
from arrow import ParserError
from qiime2 import Metadata
from .utils import strict_parse


def check_cols_present(df, required_cols):
    """Checks that a collection of columns are all present in a DataFrame."""

    if len(required_cols & set(df.columns)) < len(required_cols):
        raise ValueError(
            "Input metadata file must include the following "
            "columns: {}".format(required_cols)
        )


def check_cols_not_present(df, disallowed_cols):
    """Checks that a collection of columns are all absent from a DataFrame."""

    if len(disallowed_cols & set(df.columns)) > 0:
        raise ValueError(
            "Input metadata file already includes at least one of the "
            "following columns: {}".format(disallowed_cols)
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

    def get_time_validity(row):
        try:
            strict_parse(row["collection_timestamp"])
            # If strict_parse() didn't fail, the timestamp should be valid
            return "True"
        except ParserError:
            return "False"

    # 1. Add on is_collection_timestamp_valid column
    # Use of apply() over a basic loop based on
    # https://engineering.upside.com/a-beginners-guide-to-optimizing-pandas-code-for-speed-c09ef2c6a4d6
    m_df["is_collection_timestamp_valid"] = m_df.apply(
        get_time_validity, axis=1
    )

    # 2. Add ordinal timestamp for all samples

    def get_ordinal_timestamp(row):
        if row["is_collection_timestamp_valid"] == "True":
            parsed_date = strict_parse(row["collection_timestamp"])
            return parsed_date.isoformat().replace("-", "")
        else:
            return "not applicable"

    m_df["ordinal_timestamp"] = m_df.apply(get_ordinal_timestamp, axis=1)

    # 3. Add days elapsed

    # 3.1. Compute earliest date
    min_date = None
    for sample_id in m_df.index:
        if m_df.loc[sample_id, "is_collection_timestamp_valid"] == "True":
            parsed_date = strict_parse(
                str(m_df.loc[sample_id, "collection_timestamp"])
            )
            if min_date is None or parsed_date < min_date:
                min_date = parsed_date

    print("Earliest date is {}.".format(min_date))

    # 3.2. Assign "days from first timestamp" metric for each sample
    # (the sample(s) taken on min_date should have a value of 0, and samples
    # taken exactly a day later would have a value of 1, ...)
    # There is some inherent imprecision here due to different levels of
    # precision in sample collection (e.g. down to the day vs. down to the
    # minute), but this should be sufficient for exploratory visualization.
    m_df["days_since_first_day"] = "not applicable"

    for sample_id in m_df.index:
        if m_df.loc[sample_id, "is_collection_timestamp_valid"] == "True":
            parsed_date = strict_parse(
                str(m_df.loc[sample_id, "collection_timestamp"])
            )
            # Note the avoidance of relativedelta -- see
            # https://stackoverflow.com/a/48262147/10730311
            days_since = (parsed_date - min_date).days
            m_df.loc[sample_id, "days_since_first_day"] = str(days_since)

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

    # First off, load the metadata file and convert it to a DataFrame
    m = Metadata.load(input_metadata_file)
    m_df = m.to_dataframe()

    # ... Actually do relevant computations
    m_df_new = _add_extra_cols(m_df)

    # Convert modified DataFrame back into a q2 Metadata object and save it
    Metadata(m_df_new).save(output_metadata_file)


if __name__ == "__main__":
    add_columns()

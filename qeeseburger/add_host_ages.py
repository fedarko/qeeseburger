#! /usr/bin/env python3
import click
from arrow import ParserError
from qiime2 import Metadata
from .utils import strict_parse, check_cols_present, check_cols_not_present


def _add_host_ages(metadata_df, host_ids, host_birthdays):
    """Returns a DataFrame with a host_age_years column added."""

    m_df = metadata_df.copy()
    check_cols_present(m_df, {"collection_timestamp"})
    check_cols_not_present(m_df, {"host_age_years"})

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
    "-h",
    "--host-id-list",
    required=True,
    help="List of host subject IDs, separated by commas.",
    type=str,
)
@click.option(
    "-b",
    "--host-birthday-list",
    required=True,
    help=(
        "List of host birthdays, separated by commas. Each birthday should be "
        "in YYYYMMDD format."
    ),
    type=str,
)
@click.option(
    "-o",
    "--output-metadata-file",
    required=True,
    help="Output metadata filepath. Will contain a host_age_years column.",
    type=str,
)
def add_ages(
    input_metadata_file, host_id_list, host_birthday_list, output_metadata_file
) -> None:
    """Add host age in years on to a metadata file."""

    # First off, load the metadata file and convert it to a DataFrame
    m = Metadata.load(input_metadata_file)
    m_df = m.to_dataframe()

    # ... Actually do relevant computations
    m_df_new = _add_host_ages(m_df, host_id_list, host_birthday_list)

    # Convert modified DataFrame back into a q2 Metadata object and save it
    Metadata(m_df_new).save(output_metadata_file)


if __name__ == "__main__":
    add_ages()

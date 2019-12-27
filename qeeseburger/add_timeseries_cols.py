#! /usr/bin/env python3
import click
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from qiime2 import Metadata


def _add_extra_cols(host_subject_id, host_birthday, metadata_df):
    """Returns a DataFrame modified as expected."""

    host_birthday_datetime = parse(host_birthday)

    m_df = metadata_df.copy()
    required_cols = {"host_subject_id", "collection_timestamp"}
    if len(required_cols & set(m_df.columns)) < len(required_cols):
        raise ValueError(
            "Input metadata file must include the following "
            "columns: {}".format(required_cols)
        )

    output_cols = {
        "host_age_years",
        "ordinal_timestamp",
        "days_since_first_day",
        "is_collection_timestamp_valid",
    }
    if len(output_cols & set(m_df.columns)) > 0:
        raise ValueError(
            "Input metadata file already includes at least one of the "
            "following columns: {}".format(output_cols)
        )

    m_df["is_collection_timestamp_valid"] = "not applicable"

    # Add on is_collection_timestamp_valid column
    for sample_id in m_df.index:
        sample_timestamp = m_df["collection_timestamp"][sample_id]
        try:
            sample_datetime = parse(str(sample_timestamp))
            m_df.loc[sample_id, "is_collection_timestamp_valid"] = "True"
        except (ValueError, TypeError):
            m_df.loc[sample_id, "is_collection_timestamp_valid"] = "False"
            print(
                'WEIRD TIMESTAMP: "{}" for sample {}'.format(
                    sample_timestamp, sample_id
                )
            )

    m_df["host_age_years"] = "not applicable"

    for sample_id in m_df.index:
        # We only compute age for samples with the specified host_subject_id
        if m_df.loc[sample_id, "host_subject_id"] == host_subject_id:
            if m_df.loc[sample_id, "is_collection_timestamp_valid"] == "True":
                # Parse sample timestamp
                sample_timestamp = m_df["collection_timestamp"][sample_id]
                sample_datetime = parse(str(sample_timestamp))

                rd = relativedelta(sample_datetime, host_birthday_datetime)
                # Sanity check: the birthday should occur before a timestamp
                # (...at least, we're making the assumption that all of the
                # host subject's samples were taken after the individual in
                # question was born)
                if sample_datetime >= host_birthday_datetime:
                    m_df.loc[sample_id, "host_age_years"] = str(rd.years)
                else:
                    raise ValueError(
                        (
                            "Sample {} has a collection_timestamp, {}, "
                            "occurring before the host birthday of {}."
                        ).format(sample_id, sample_timestamp, host_birthday)
                    )

    # 2. Add ordinal timestamp for all samples

    m_df["ordinal_timestamp"] = "not applicable"

    for sample_id in m_df.index:
        if m_df.loc[sample_id, "is_collection_timestamp_valid"] == "True":
            parsed_date = parse(
                str(m_df.loc[sample_id, "collection_timestamp"])
            )
            parsed_date_ordinalstring = parsed_date.isoformat()[:10].replace(
                "-", ""
            )
            m_df.loc[
                sample_id, "ordinal_timestamp"
            ] = parsed_date_ordinalstring

    # 3. Add days elapsed

    # 3.1. Compute earliest date
    min_date = None
    for sample_id in m_df.index:
        if m_df.loc[sample_id, "is_collection_timestamp_valid"] == "True":
            parsed_date = parse(
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
            parsed_date = parse(
                str(m_df.loc[sample_id, "collection_timestamp"])
            )
            # Note the avoidance of relativedelta -- see
            # https://stackoverflow.com/a/48262147/10730311
            days_since = (parsed_date - min_date).days
            m_df.loc[sample_id, "days_since_first_day"] = str(days_since)

    return m_df


@click.command()
@click.option(
    "-hsid",
    "--host-subject-id",
    required=True,
    help="Host subject ID to set age for.",
    type=str,
)
@click.option(
    "-b",
    "--host-birthday",
    required=True,
    help=(
        "Birthday used for setting age. Must be in a format understood by "
        "dateutil.parser.parse()."
    ),
    type=str,
)
@click.option(
    "-i",
    "--input-metadata-file",
    required=True,
    help=(
        "Input metadata filepath. Must contain collection_timestamp and "
        "host_subject_id columns."
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
def add_columns(
    host_subject_id, host_birthday, input_metadata_file, output_metadata_file
) -> None:
    """Add some useful columns for time-series studies to a metadata file.

    In particular, the columns added are "is_collection_timestamp_valid",
    "host_age_years", "ordinal_timestamp", and "days_since_first_day".
    """

    # First off, load the metadata file and convert it to a DataFrame
    m = Metadata.load(input_metadata_file)
    m_df = m.to_dataframe()

    # ... Actually do relevant computations
    m_df_new = _add_extra_cols(host_subject_id, host_birthday, m_df)

    Metadata(m_df_new).save(output_metadata_file)


if __name__ == "__main__":
    add_columns()

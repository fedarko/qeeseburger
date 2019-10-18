#! /usr/bin/env python3
import click
import pandas as pd
from dateutil.parser import parse
from qiime2 import Metadata


@click.command()
@click.option(
    "-hsid",
    "--host-subject-id",
    required=True,
    help="Host subject ID to set dietary phase for.",
    type=str,
)
@click.option(
    "-p",
    "--phase-name",
    required=True,
    help="Key word to look for in dietary phases. Any rows in the key dates "
    "spreadsheet where the 'Event' column contains the text 'Started "
    "PHASENAME' or 'Stopped PHASENAME', where PHASENAME is the string you "
    "specify here, will be treated as start/end range(s) for that phase.",
    type=str,
)
@click.option(
    "-k",
    "--key-dates-spreadsheet",
    required=True,
    help=(
        "Filepath to an Excel spreadsheet containing dates as the first "
        "column and 'Event' as the second column."
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
    help=(
        "Output metadata filepath. Will contain a new column named with "
        "whatever you set the -p option to."
    ),
    type=str,
)
def add_dietary_phase(
    host_subject_id,
    phase_name,
    key_dates_spreadsheet,
    input_metadata_file,
    output_metadata_file,
) -> None:
    """Encodes dietary phase information into a sample metadata file.

    The main information needed for this are the phase name (-p) and the key
    dates spreadsheet (-k). This program looks for rows in the key dates
    spreadsheet where the "Event" column contains the text "Started PHASENAME"
    or "Stopped PHASENAME", where PHASENAME is just the string you specified in
    the -p option.
    
    This program will then use the dates associated with these rows to
    determine ranges of dates for which the given dietary phase was being
    followed -- this is useful if the subject went on and off a diet multiple
    times.

    Finally, this will add a PHASENAME column to the metadata file. Samples
    will be assigned one of three possible values in this column:

        Samples where host_subject_id is equal to the -hsid parameter AND the
        collection_timestamp falls within a dietary phase range will be
        labelled "TRUE".

        Samples where host_subject_id is equal to the -hsid parameter AND the
        collection_timestamp DOES NOT fall within a dietary phase range will
        be labelled "FALSE".

        Samples where host_subject_id is NOT EQUAL to the -hsid parameter
        will be labelled "not applicable".

    This only treats dates as down to the day. So if the subject started a diet
    at 12pm on a day and then ended that diet at 5pm that same day, this code
    will treat both of these dates as occurring on the same day and thus raise
    an error.
    """

    m = Metadata.load(input_metadata_file)
    m_df = m.to_dataframe()

    # Validate the input metadata file, somewhat
    required_cols = {"host_subject_id", "collection_timestamp"}
    if len(required_cols & set(m_df.columns)) < len(required_cols):
        raise ValueError(
            "Input metadata file must include the following columns: "
            "{}".format(required_cols)
        )
    if phase_name in m_df.columns:
        raise ValueError(
            "A {} column already exists in the input metadata!".format(phase_name)
        )

    # Validate the key dates spreadsheet, somewhat
    kd = pd.read_excel(key_dates_spreadsheet, index_col=0)
    # I didn't actually know this functionality existed until I saw this SO
    # answer: https://stackoverflow.com/a/57187654/10730311
    if not pd.api.types.is_datetime64_any_dtype(kd.index):
        raise ValueError(
            "First column of the key dates spreadsheet must contain dates/timestamps"
        )
    if "Event" not in kd.columns:
        raise ValueError('Key dates spreadsheet must contain an "Event" column')

    # Determine ranges for starting/stopping a given diet (this requires a
    # decent amount of validation)
    starting_dates = kd.loc[kd["Event"].str.find("Started {}".format(phase_name)) >= 0]
    if len(starting_dates.index) < 1:
        raise ValueError("No starting dates for the specified phase given")

    stopping_dates = kd.loc[kd["Event"].str.find("Stopped {}".format(phase_name)) >= 0]
    if len(stopping_dates.index) < 1:
        raise ValueError("No stopping dates for the specified phase given")

    if len(starting_dates.index) != len(stopping_dates.index):
        raise ValueError(
            "Number of starting/stopping dates must be consistent (if the "
            "phase continues to the final sample, then you'll need to add a "
            "stoppping row for the day of or after that sample)"
        )

    # We now know that we have an equal (and >= 1) number of starting and
    # stopping dates, but we'd like to know if the dates actually make sense.
    #
    # This necessitates checking that every stopping date occurs later than its
    # corresponding starting date, *and* ensuring that every starting date
    # occurs later than the previous stopping date (i.e. the ranges are in
    # chronological order)
    #
    # You can think of this graphically as something like:
    #
    # A1---B1 A2--B2     A3B3 A4-----B4  A5-B5 A6--B6
    #
    # where each A is a starting date and each B is a stopping date. Notice how
    # these ranges are not overlapping, so they can just be represented as a
    # single line -- this is what we're checking for here.
    for i in range(len(starting_dates.index)):
        # NOTE: we use .date() to just get the date, not the timestamp, of
        # datetimes. This lets us do comparisons only down to the day level.
        # Thanks to https://stackoverflow.com/a/13227661/10730311.
        da = starting_dates.iloc[i].name.date()
        db = stopping_dates.iloc[i].name.date()
        if da >= db:
            raise ValueError(
                "Starting date {} occurs later or on same day as "
                "corresponding stopping date {}.".format(da, db)
            )
        if i > 0:
            prev_db = stopping_dates.iloc[i - 1].name.date()
            if da <= prev_db:
                raise ValueError(
                    "Starting date {} occurs earlier or on same day as "
                    "previous stopping date {}.".format(da, prev_db)
                )

    # OK, now we know the ranges are good! We're done validating the inputs at
    # this point.

    m_df[phase_name] = "not applicable"

    for sample_id in m_df.index:
        if m_df.loc[sample_id, "host_subject_id"] == host_subject_id:
            # Parse sample timestamp
            sample_date = parse(m_df["collection_timestamp"][sample_id]).date()

            # If the sample was collected before any of the ranges, then we'll
            # never get into the first "if" statement in the for loop below.
            # That's fine; in this case, the sample doesn't fall in any of the
            # ranges, so we can safely leave its value as FALSE.
            in_phase = "FALSE"

            # Iterate backwards through ranges
            for ii in range(len(starting_dates.index))[::-1]:
                if sample_date >= starting_dates.iloc[ii].name.date():
                    if sample_date <= stopping_dates.iloc[ii].name.date():
                        in_phase = "TRUE"
                        break
                    else:
                        # We know that this sample occurred after the current
                        # range. Furthermore, we're looking at the ranges in
                        # descending order, so we know that the sample wasn't
                        # in any ranges after this one. Therefore, we can
                        # conclusively say that this sample is not present in
                        # any ranges.
                        break

            m_df.loc[sample_id, phase_name] = in_phase

        # For samples where the host subject ID *does not* match the one
        # specified, the phase_name value will be left as "not applicable"

    # Cool, we're done!

    Metadata(m_df).save(output_metadata_file)


if __name__ == "__main__":
    add_dietary_phase()

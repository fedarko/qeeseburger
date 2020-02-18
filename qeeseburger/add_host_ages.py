#! /usr/bin/env python3
import click
from dateutil.relativedelta import relativedelta
from arrow import ParserError
from .utils import (
    strict_parse,
    check_cols_present,
    check_cols_not_present,
    manipulate_md,
)


APPROXIMATE_YEAR_LENGTH_IN_DAYS = 365.2422


def _add_host_ages(metadata_df, host_ids, host_birthdays, float_years=False):
    """Returns a DataFrame with a "host age" column added on.

       If float_years is False, the new column will be named
       "host_age_years", and will contain just the host age down to the year.

       If float_years is True, the new column will instead be named
       "host_age", and will contain an APPROXIMATION of the host
       age in float years by dividing the age in days by 365.2422, and
       truncating the result to 4 decimal points.
       Note the whole APPROXIMATION thing in the previous sentence -- this is
       kind of a hack, and is mostly intended for use in "comparisons". (And
       for doing Emperor animations and stuff like that, you should really just
       use the days_since_first_day column that add-ts-cols gives you.)

       IN EITHER CASE, the values will be represented in the DataFrame as
       strings.

       As an example: if a host's birthday is on December 1, 1990 and
       there's a sample from November 20, 1995 from that host:
        - that sample's "host_age_years" value will be 4
        - that sample's "host_age" value will be 4.9693
    """

    m_df = metadata_df.copy()

    if float_years:
        output_col_name = "host_age"
    else:
        output_col_name = "host_age_years"

    # Validate input a bit
    check_cols_present(m_df, {"collection_timestamp", "host_subject_id"})
    check_cols_not_present(m_df, {output_col_name})

    host_id_list = [i.strip() for i in host_ids.split(",")]
    host_bday_list = [i.strip() for i in host_birthdays.split(",")]

    for t in (host_id_list, host_bday_list):
        if len(t) == 0 or (len(t) == 1 and t[0] == ""):
            raise ValueError("No host IDs and/or birthdays were specified.")

    if len(host_id_list) != len(host_bday_list):
        raise ValueError(
            "Number of host IDs doesn't match number of birthdays."
        )

    if len(set(host_id_list)) != len(host_id_list):
        raise ValueError("The specified host IDs aren't unique?")

    try:
        host_bday_date_list = [strict_parse(s) for s in host_bday_list]
    except ParserError:
        raise ValueError("(Some of) the birthdays aren't correctly formatted.")

    # figure out what host has what birthday
    # precomputing this dict should save some time
    hostid2bdaydate = {}
    for i in range(len(host_id_list)):
        hostid2bdaydate[host_id_list[i]] = host_bday_date_list[i]

    def get_host_age_if_poss(row):
        sample_hostid = row["host_subject_id"]
        # Is this sample from a host we care about?
        if sample_hostid in host_id_list:
            # Try to parse sample date
            try:
                sample_date = strict_parse(str(row["collection_timestamp"]))
            except ParserError:
                # can't get the age for this sample -- timestamp is invalid
                return "not applicable"
            # Check that the date actually occurs after/on the sample's host's
            # birthday...
            host_bday_date = hostid2bdaydate[sample_hostid]
            if sample_date >= host_bday_date:
                # Success! Return the age in (integer or float) years expressed
                # as a string
                if float_years:
                    return "{:.4f}".format(
                        (sample_date - host_bday_date).days
                        / APPROXIMATE_YEAR_LENGTH_IN_DAYS
                    )
                else:
                    return str(
                        relativedelta(sample_date, host_bday_date).years
                    )
            else:
                print(
                    "Sample {} has a timestamp date, {}, occurring before the "
                    "host birthday date of {}.".format(
                        row.name, sample_date, host_bday_date
                    )
                )
                return "impossible"
        else:
            return "not applicable"

    m_df[output_col_name] = m_df.apply(get_host_age_if_poss, axis=1)
    return m_df


@click.command()
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
        "in YYYY-MM-DD format, and the number of birthdays should match the "
        "number of host IDs specified."
    ),
    type=str,
)
@click.option(
    "--float-years",
    is_flag=True,
    help=(
        "If this flag is used, the host ages will be in float approximations "
        "(using day-level precision) instead of integers down to the year."
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
def add_host_ages(
    input_metadata_file,
    host_id_list,
    host_birthday_list,
    float_years,
    output_metadata_file,
) -> None:
    """Add host age in years on to a metadata file.

       The column added will be named "host_age_years" if --float-years isn't
       set, and "host_age" if --float-years *is* set.
    """

    manipulate_md(
        input_metadata_file,
        [host_id_list, host_birthday_list, float_years],
        output_metadata_file,
        _add_host_ages,
    )


if __name__ == "__main__":
    add_host_ages()

import arrow


def strict_parse(
    timestamp,
    expected_formats=[
        "YYYY-MM-DD",
        "YYYY-M-D",
        "MM/DD/YYYY",
        "M/D/YYYY",
        "M/D/YY",
        # Idiosyncratic formats needed to parse some timestamps I've run into
        "[']YYYY-MM-DD",
        "YYYY-MM-DD[:]",
    ],
):
    """Parses a timestamp; only succeeds if it contains a year, month, and day.

       This function is intended to be more strict than many publicly
       available timestamp parsers, which accept timestamps that don't
       explicitly specify days or months like "2012" or "2012-10". For
       Qeeseburger (as of writing, at least), we require that each timestamp
       at least specifies precision down to the day. (Cases like "2012-10"
       should be flagged as invalid timestamps; we can't do much with these,
       and in my opinion it makes sense to exclude these from longitudinal
       studies where we have the benefit of a lot of samples, at least for
       now.*)

       TLDR: This basically just calls arrow.get(), but I had to go through
       like 3 other libraries before I found something that did what I wanted
       (and even then I still think this solution is harder than it should be).

       Parameters
       ----------

       timestamp: str
            A string representation of a sample's timestamp.

       expected_formats: list of str
            A list of formats to try parsing the timestamp with. This list will
            be passed into arrow.get() as is. YOU WILL PROBABLY WANT TO EXTEND
            THIS LIST if you're going to be parsing arbitrary dates with this
            thing -- these formats are suitable for my use cases right now, but
            not comprehensive.

       Returns
       -------

       datetime.date
            If parsing succeeded, this returns one of these objects with a
            specified year, month, and day. Note that even if you pass in a
            timestamp with more precise information (e.g. hour, minute, second,
            time zone, ...) this'll be ignored -- we only consider the date.

       Raises
       ------

       arrow.ParserError: if arrow.get() can't parse the input timestamp using
                          the expected_formats. For huge datasets with some
                          incomplete or otherwise funky timestamps, this is to
                          be expected -- this case should be handled
                          appropriately.
    """
    arrow_obj = arrow.get(timestamp, expected_formats)
    # If that didn't fail, then Arrow was able to parse the timestamp! Yay.
    return arrow_obj.date()

# Qeeseburger

<div align="center">
<img width="60%" src="https://raw.githubusercontent.com/fedarko/qeeseburger/master/images/logo.png" alt="Qeeseburger logo" />
</div>

<div align="center">
<a href="https://travis-ci.com/fedarko/qeeseburger"><img src="https://travis-ci.com/fedarko/qeeseburger.svg?branch=master" alt="Build Status" /></a>
<a href="https://codecov.io/gh/fedarko/qeeseburger"><img src="https://codecov.io/gh/fedarko/qeeseburger/branch/master/graph/badge.svg" alt="Code Coverage" /></a>
<p>(Pronounced "cheeseburger.")
</div>

This repository contains some basic scripts that I've written for dealing
with time series microbiome and dietary/medical data. This might be turned into
a more official python package sometime in the future, depending on how this
codebase evolves.

## Installation
```bash
# This assumes you're already in a QIIME 2 conda environment
pip install git+https://github.com/fedarko/qeeseburger.git
```

Once installing Qeeseburger, a few scripts will be available:

## 1. `add-ts-cols`

This script adds some useful columns to a QIIME 2 compatible metadata file and
writes out a new file.

The columns added:
1. `is_collection_timestamp_valid`
2. `ordinal_timestamp`
3. `days_since_first_day`

### Usage
```
$ add-ts-cols --help
Usage: add-ts-cols [OPTIONS]

  Add some useful columns for time-series studies to a metadata file.

  In particular, the columns added are "is_collection_timestamp_valid",
  "ordinal_timestamp", and "days_since_first_day".

  Note that the value of days_since_first_day may vary even between samples
  with identical collection_timestamp values if you run this script on
  different metadata files. This is because the "first day" is computed
  relative to all of the valid collection_timestamps in the input metadata
  file; to ensure that the values in this column are comparable between
  datasets, you should merge metadata and then run this script.

Options:
  -i, --input-metadata-file TEXT  Input metadata filepath. Must contain a
                                  collection_timestamp column.  [required]
  -o, --output-metadata-file TEXT
                                  Output metadata filepath. Will contain some
                                  additional columns.  [required]
  --help                          Show this message and exit.
```

### References
This is based on some gists I've written before:
1. [`convert_timestamp_to_ordinal_date.py`](https://gist.github.com/fedarko/05222da5b3f01ce9d77c6b989cf4d881)
2. [`convert_timestamp_to_days_elapsed.py`](https://gist.github.com/fedarko/647241b3f06ca76c1ccb6bcbd7fc778d)

## 2. `add-host-ages`

Similar to `add-ts-cols`, this script adds in a `host_age_years` column to a
metadata file. You can specify multiple host IDs/birthdays in comma-separated
lists, so this is useful for timeseries datasets where you have multiple
subjects.

Note that this doesn't change any other columns (e.g. `host_age_units`, another
common column for Qiita metadata files). Updating that column is up to you (at least
as of now).

### Usage
```
Usage: add-host-ages [OPTIONS]

  Add host age in years on to a metadata file.

  The column added will be named "host_age_years" if --float-years isn't
  set, and "host_age" if --float-years *is* set.

Options:
  -i, --input-metadata-file TEXT  Input metadata filepath. Must contain
                                  collection_timestamp and host_subject_id
                                  columns.  [required]
  -h, --host-id-list TEXT         List of host subject IDs, separated by
                                  commas.  [required]
  -b, --host-birthday-list TEXT   List of host birthdays, separated by commas.
                                  Each birthday should be in YYYY-MM-DD
                                  format, and the number of birthdays should
                                  match the number of host IDs specified.
                                  [required]
  --float-years                   If this flag is used, the host ages will be
                                  in float approximations (using day-level
                                  precision) instead of integers down to the
                                  year.
  -o, --output-metadata-file TEXT
                                  Output metadata filepath. Will contain a
                                  host_age_years column.  [required]
  --help                          Show this message and exit.
```

### References
This is based on this gist I wrote a while back:
1. [`add_age_column_to_metadata.py`](https://gist.github.com/fedarko/49088da6bba5705f987192a954b2416f)

## 3. `add-diet`

This is a more complicated script. Essentially, it looks at an Excel
spreadsheet containing dietary/drug information (e.g. "Started Diet A", "Stopped
Diet A", ...) and encodes this information as a column in a metadata file. This
is particularly useful if the same diet was started and stopped multiple times.

Note that this makes a few assumptions, in particular:
1. **That the dates in the spreadsheet are only precise down to the day.**
2. **That "Stopped Diet A" dates do not count as days where that diet was followed:** that is, this treats the end-dates of dietary ranges in an "exclusive" manner.

### Usage
```
$ add-diet --help
Usage: add-diet [OPTIONS]

  Encodes dietary phase information into a sample metadata file.

  The main information needed for this are the phase name (-p) and the key
  dates spreadsheet (-k). This program looks for rows in the key dates
  spreadsheet where the "Event" column contains the text "Started PHASENAME"
  or "Stopped PHASENAME", where PHASENAME is just the string you specified
  in the -p option.

  This program will then use the dates associated with these rows to
  determine ranges of dates for which the given dietary phase was being
  followed -- this is useful if the subject went on and off a diet multiple
  times. The start date of a phase is counted as being in that range; the
  end date is NOT counted as being in that range.

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

  This only treats dates as down to the day. So if the subject started a
  diet at 12pm on a day and then ended that diet at 5pm that same day, this
  code will treat both of these dates as occurring on the same day and thus
  raise an error.

Options:
  -hsid, --host-subject-id TEXT   Host subject ID to set dietary phase for.
                                  [required]
  -p, --phase-name TEXT           Key word to look for in dietary phases. Any
                                  rows in the key dates spreadsheet where the
                                  'Event' column contains the text 'Started
                                  PHASENAME' or 'Stopped PHASENAME', where
                                  PHASENAME is the string you specify here,
                                  will be treated as start/end range(s) for
                                  that phase (these ranges are assumed to be
                                  inclusive for the start date and exclusive
                                  on the end date).  [required]
  -k, --key-dates-spreadsheet TEXT
                                  Filepath to an Excel spreadsheet containing
                                  dates as the first column and 'Event' as the
                                  second column.  [required]
  -i, --input-metadata-file TEXT  Input metadata filepath. Must contain
                                  collection_timestamp and host_subject_id
                                  columns.  [required]
  -o, --output-metadata-file TEXT
                                  Output metadata filepath. Will contain a new
                                  column named with whatever you set the -p
                                  option to.  [required]
  --help                          Show this message and exit.
```

### Disclaimer

This script is not yet covered by automatic testing;
if you notice something funky with the
output or behavior of this code, it's likely a bug -- feel free to open an
issue, PR, etc.

## Dependencies

- [Arrow](https://arrow.readthedocs.io/)
- [Click](http://click.palletsprojects.com/)
- [dateutil](https://dateutil.readthedocs.io/)
- [pandas](https://pandas.pydata.org/)
- [QIIME 2 (this uses the "Artifact API")](https://qiime2.org/)

## Acknowledgements

- [I created the logo for this by butchering the QIIME 2 logo, sorry](https://qiime2.org/)
- [This guide that I always come back to for centering things in GitHub markdown](https://gist.github.com/DavidWells/7d2e0e1bc78f4ac59a123ddf8b74932d)

## Why did you name this tool "Qeeseburger"?
Honestly, I really just wanted to name something "Qeeseburger." In that
respect, this code is already a success.

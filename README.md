# Qeeseburger

<div align="center">
<img width="60%" src="https://raw.githubusercontent.com/fedarko/qeeseburger/master/docs/images/logo.png" alt="Qeeseburger logo" />
</div>

This repository contains some basic scripts/etc. that I've written for dealing
with time series microbiome/biomarker data. This might be turned into an
actual python package and/or QIIME 2 plugin sometime in the future, depending
on how this codebase evolves.

## `add_age_and_extra_times.py`

This script adds some useful columns to a QIIME 2 compatible metadata file and
writes out a new file. This isn't really anything fancy, and the code is pretty
inefficient because it's really just three separate scripts glued together.

This is based on three gists I've written before:
1. [`add_age_column_to_metadata.py`](https://gist.github.com/fedarko/49088da6bba5705f987192a954b2416f)
2. [`convert_timestamp_to_ordinal_date.py`](https://gist.github.com/fedarko/05222da5b3f01ce9d77c6b989cf4d881)
3. [`convert_timestamp_to_days_elapsed.py`](https://gist.github.com/fedarko/647241b3f06ca76c1ccb6bcbd7fc778d)

## `add_dietary_phase.py`

This is a more complicated script. Essentially, it looks at an Excel
spreadsheet containing dietary information (e.g. "Started Diet A", "Stopped
Diet A", ...) and encodes this information as a column in a metadata file. This
is particularly useful if the same diet was started and stopped multiple times.

Note that this makes a few assumptions, in particular:
1. **That the dates in the spreadsheet are only precise down to the day.**
2. **That "Stopped Diet A" dates still count as days where that diet was followed.**

## Disclaimer

Although I've looked at the outputs of this code manually, I don't have any
automatic testing set up for it (yet). If you notice something funky with the
output or behavior of this code, it's likely a bug -- feel free to raise an
issue, PR, etc.

## Dependencies

- [Click](http://click.palletsprojects.com/)
- [dateutil](https://dateutil.readthedocs.io/en/stable/)
- [pandas](https://pandas.pydata.org/)
- [QIIME 2 (this uses the "Artifact API")](https://qiime2.org/)

## Acknowledgements

- [This guide that I always come back to for centering things in GitHub markdown](https://gist.github.com/DavidWells/7d2e0e1bc78f4ac59a123ddf8b74932d)

## Why did you name this tool "Qeeseburger"?
Honestly, I really just wanted to name something "Qeeseburger." In that
respect, this code is already a success.

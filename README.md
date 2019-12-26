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
writes out a new file. This isn't really anything fancy, and the code is pretty
inefficient because it's really just three separate scripts glued together.

The columns added:
1. `is_collection_timestamp_valid`
2. `host_age_years`
3. `ordinal_timestamp`
4. `days_since_first_day`

### References
This is based on three gists I've written before:
1. [`add_age_column_to_metadata.py`](https://gist.github.com/fedarko/49088da6bba5705f987192a954b2416f)
2. [`convert_timestamp_to_ordinal_date.py`](https://gist.github.com/fedarko/05222da5b3f01ce9d77c6b989cf4d881)
3. [`convert_timestamp_to_days_elapsed.py`](https://gist.github.com/fedarko/647241b3f06ca76c1ccb6bcbd7fc778d)

## 2. `add-diet`

This is a more complicated script. Essentially, it looks at an Excel
spreadsheet containing dietary/drug information (e.g. "Started Diet A", "Stopped
Diet A", ...) and encodes this information as a column in a metadata file. This
is particularly useful if the same diet was started and stopped multiple times.

Note that this makes a few assumptions, in particular:
1. **That the dates in the spreadsheet are only precise down to the day.**
2. **That "Stopped Diet A" dates do not count as days where that diet was followed:** that is, this treats the end-dates of dietary ranges in an "exclusive" manner.

### Disclaimer

This script is not yet covered by automatic testing;
if you notice something funky with the
output or behavior of this code, it's likely a bug -- feel free to open an
issue, PR, etc.

## Dependencies

- [Click](http://click.palletsprojects.com/)
- [dateutil](https://dateutil.readthedocs.io/en/stable/)
- [pandas](https://pandas.pydata.org/)
- [QIIME 2 (this uses the "Artifact API")](https://qiime2.org/)

## Acknowledgements

- [I created the logo for this by butchering the QIIME 2 logo, sorry](https://qiime2.org/)
- [This guide that I always come back to for centering things in GitHub markdown](https://gist.github.com/DavidWells/7d2e0e1bc78f4ac59a123ddf8b74932d)

## Why did you name this tool "Qeeseburger"?
Honestly, I really just wanted to name something "Qeeseburger." In that
respect, this code is already a success.

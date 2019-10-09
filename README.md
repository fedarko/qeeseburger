# Qeeseburger

This repository contains some basic scripts/etc. that I've written for dealing
with time series microbiome/biomarker data. This might be turned into an
actual python package and/or QIIME 2 plugin sometime in the future, depending
on how this codebase evolves.

## `qeeseburger.py`

This script adds some useful columns to a QIIME 2 compatible metadata file and
writes out a new file. This isn't really anything fancy, and the code is pretty
inefficient because it's really just three separate scripts glued together.

This is based on three gists I've written before:
1. [`add_age_column_to_metadata.py`](https://gist.github.com/fedarko/49088da6bba5705f987192a954b2416f)
2. [`convert_timestamp_to_ordinal_date.py`](https://gist.github.com/fedarko/05222da5b3f01ce9d77c6b989cf4d881)
3. [`convert_timestamp_to_days_elapsed.py`](https://gist.github.com/fedarko/647241b3f06ca76c1ccb6bcbd7fc778d)

## Why did you name this tool "Qeeseburger"?
Honestly, I really just wanted to name something "Qeeseburger." In that
respect, this code is already a success.

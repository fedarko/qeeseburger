# NOTE: This is based on Qurro's Makefile.
.PHONY: test pytest jstest stylecheck style

test:
	python3 -B -m pytest qeeseburger/tests --cov qeeseburger

stylecheck:
	flake8 qeeseburger/ setup.py
	black --check -l 79 qeeseburger/ setup.py

style:
	black -l 79 qeeseburger/ setup.py

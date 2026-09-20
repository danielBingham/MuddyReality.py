#!/bin/bash
####
# A simple script to lint, test and validate MuddyReality.py in one go.
#
# Every step runs, whether or not the ones before it passed, so that one run
# shows everything that needs fixing.  The script exits non-zero if any of
# them failed.
###

status=0

echo "Running flake8 to validate code..."
flake8 . || status=1

echo "Running pytest to run unit tests..."
pytest tests || status=1

echo "Running the data validator to load and validate the data library..."
python3 main.py validator || status=1

exit $status

#!/bin/bash
####
# A simple script to lint and test MuddyReality.py in one go.
###

echo "Running flake8 to validate code..."
flake8 .

echo "Running pytest to run unit tests..."
pytest tests

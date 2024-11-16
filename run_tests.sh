#!/bin/bash
# Install dependencies and run tests

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

chmod +x run_tests.sh

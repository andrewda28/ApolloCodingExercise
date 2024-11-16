#!/bin/bash
# Run the Flask application

# Activate virtual environment
source venv/bin/activate

# Export environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the application
flask run --port=5000

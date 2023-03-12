#!/bin/bash
set -e

# Wait for the database to be ready
wait-for-it excel-app-db:5432 --timeout=30 --strict -- echo "Database is up"

# Start your app
python run.py

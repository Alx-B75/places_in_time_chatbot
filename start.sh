#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Run the database initialization script
echo "--- Running database initialization ---"
python backend/init_db.py

# Start the Uvicorn server
echo "--- Starting Uvicorn server ---"
uvicorn backend.main:app --host 0.0.0.0 --port 10000
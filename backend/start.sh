#!/bin/bash

# Wait for PostgreSQL
while ! nc -z db 5432; do
    echo "Waiting for PostgreSQL to start..."
    sleep 1
done

# Wait for Temporal
while ! nc -z temporal 7233; do
    echo "Waiting for Temporal to start..."
    sleep 1
done

# Start Temporal worker in the background
python temporal_worker.py &

# Start FastAPI server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload 
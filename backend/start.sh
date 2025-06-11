#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload 
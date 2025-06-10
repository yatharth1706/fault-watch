# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 1. Copy pyproject.toml and lockfile
COPY pyproject.toml uv.lock /app/

# 2. Install dependencies via uv
RUN pip install uv && uv sync

# 3. Copy the entire backend source (here api/) into /app/backend
#    (If your code directory is named api/, adjust accordingly.)
COPY . /app/backend

WORKDIR /app/backend

EXPOSE 8000

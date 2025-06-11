# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 1. Copy pyproject.toml and lockfile
COPY pyproject.toml uv.lock /app/

# 2. Install dependencies via uv
RUN pip install uv && uv sync

# 3. Create backend directory for volume mount
RUN mkdir -p /app/backend

WORKDIR /app/backend

# 4. Activate the virtual environment and expose port
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

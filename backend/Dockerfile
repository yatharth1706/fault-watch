# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install netcat for database connectivity checks
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# 1. Copy pyproject.toml and lockfile
COPY pyproject.toml uv.lock /app/

# 2. Install dependencies via uv
RUN pip install uv && uv sync

# 3. Create backend directory for volume mount
RUN mkdir -p /app/backend

WORKDIR /app/backend

# 4. Copy start.sh and give it execute permissions
COPY start.sh /app/backend/start.sh
RUN chmod +x /app/backend/start.sh

# 5. Activate the virtual environment and expose port
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

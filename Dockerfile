# Stage 1: Build Stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install necessary system dependencies for asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final (Runtime) Stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for runtime (libpq-dev parts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages and binaries from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY ./app /app/app

# Expose the application port
EXPOSE 8000

# Set environment variables for configuration (defaults/placeholders)
ENV FASTAPI_ENV=production \
    DB_HOST=db \
    DB_NAME=iot_db \
    DB_USER=iot_user \
    DB_PASSWORD=iot_password \
    DB_PORT=5432

# Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

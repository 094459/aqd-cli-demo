FROM python:3.10-slim

# Build arguments
ARG VERSION="dev"
ARG BUILD_DATE="unknown"
ARG VCS_REF="unknown"

# Add labels for container metadata
LABEL org.opencontainers.image.title="Customer Survey App" \
      org.opencontainers.image.description="A web application for creating and managing customer surveys" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.authors="AWS"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi.py \
    PORT=8000 \
    APP_VERSION=${VERSION}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Create data directory for SQLite database
RUN mkdir -p /app/data && chmod 777 /app/data

# Expose port
EXPOSE ${PORT}

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

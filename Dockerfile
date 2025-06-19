# Dockerfile for DigitalOcean App Platform deployment
# Optimized for Python Discord bot with SQLite

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for SQLite and potential C++ compilation
RUN apt-get update && apt-get install -y \
    sqlite3 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY .env.example ./

# Create directory for SQLite database
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port (not needed for Discord bot but good practice)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('/app/data/wildfire_game.db').close()" || exit 1

# Run the Discord bot
CMD ["python", "src/main.py"]
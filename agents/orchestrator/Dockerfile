# Agent Orchestrator - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy orchestrator code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1001 orchestrator && chown -R orchestrator:orchestrator /app
USER orchestrator

# Expose port for API server
EXPOSE 8100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8100/health || exit 1

# Default command (can be overridden)
CMD ["python", "server.py"]
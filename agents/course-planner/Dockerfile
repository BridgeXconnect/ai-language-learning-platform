# Course Planner Agent - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1001 agent && chown -R agent:agent /app
USER agent

# Expose port for API server
EXPOSE 8101

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8101/health || exit 1

# Default command (can be overridden)
CMD ["python", "server.py"]
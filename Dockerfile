# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psutil
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    HOST=0.0.0.0 \
    PORT=5000

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "app.py"]
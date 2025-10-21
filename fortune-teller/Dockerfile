FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and directories
COPY app.py .
COPY fortunes.json .
COPY templates/ templates/
COPY static/ static/

# Create shared directory for success recording
RUN mkdir -p /shared

# Expose ports
EXPOSE 6010 5001

# Run the application
CMD ["flask", "run", "--port", "6010", "--host", "0.0.0.0"]
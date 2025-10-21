FROM python:3.11-slim

WORKDIR /usr/src/app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install common test dependencies
RUN pip install --no-cache-dir pytest==7.4.3 requests==2.31.0 pytest-json-report==1.5.0 Pillow==10.0.1 numpy

# Copy shared cleanup script to a location that won't be overwritten by mount
COPY cleanup.py /usr/local/bin/cleanup.py
RUN chmod +x /usr/local/bin/cleanup.py

# Create a shared directory for results
RUN mkdir -p /shared

# Default command to run tests from mounted directory (and I suppose we'll attempt to support Windows)
CMD sed -i "s/\r$//" run_tests.sh && chmod 755 ./run_tests.sh && ./run_tests.sh
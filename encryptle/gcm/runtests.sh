#!/bin/bash
# This file is out-of-scope for vulnerabilities. It runs the tests in docker for you.

echo "Running tests with Docker Compose..."
docker compose --profile testing up --build -d

echo "Waiting for tests to complete..."
docker compose --profile testing logs -f tests

echo "Cleaning up containers..."
docker compose --profile testing down
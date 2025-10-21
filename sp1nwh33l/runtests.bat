@echo off
REM This file runs the tests in docker for sp1nwh33l.

echo Running tests with Docker Compose...
docker compose --profile testing up --build -d

echo Waiting for tests to Complete...
docker compose --profile testing logs -f tests

echo Cleaning up containers...
docker compose --profile testing down

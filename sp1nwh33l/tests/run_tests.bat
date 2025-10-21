@echo off
REM Run tests with pytest

cd /d C:\usr\src\app
pytest --disable-warnings --json-report --json-report-file=out.json --json-report-omit keywords streams

if exist "C:\shared" (
    copy out.json C:\shared\
)

#!/bin/bash
# Run tests with pytest

cd /usr/src/app
pytest --disable-warnings --json-report --json-report-file=out.json --json-report-omit keywords streams

if [ -d "/shared" ]; then
    cp out.json /shared/
fi
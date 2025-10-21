#!/bin/bash

echo "Building Fortune Cookie Factory challenge..."

# Build the Docker image
docker build -t fortune-cookie .

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "To run the challenge: docker-compose up"
else
    echo "Build failed!"
    exit 1
fi
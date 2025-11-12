#!/bin/bash

# Build production image first
echo "Building production image..."
docker build -t hooter-the-tutor:prod .

# Build local image extending production
echo "Building local development image..."
docker build -f Dockerfile.local -t hooter-the-tutor:local .

# Run with interactive shell and volume mounting
echo "Starting local development container..."
docker run --rm -it -v "$(pwd):/app" hooter-the-tutor:local
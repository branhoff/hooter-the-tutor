#!/bin/bash

# Stop and remove the existing container if it exists
docker stop hooter-the-tutor 2>/dev/null
docker rm hooter-the-tutor 2>/dev/null

# Build the Docker image
docker build . -t hooter-the-tutor-image

# Run the Docker container
docker run -d \
  --env-file .env \
  --name hooter-the-tutor \
  --restart unless-stopped \
  hooter-the-tutor-image

# Print the container logs
echo "Container started. Printing logs:"
docker logs -f hooter-the-tutor
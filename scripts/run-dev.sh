#!/bin/bash

# Build the image
docker build -t hooter-the-tutor .

# Run container with interactive terminal and volume mounting
docker run -it --rm -v "$(pwd):/home/devuser/workspace" hooter-the-tutor
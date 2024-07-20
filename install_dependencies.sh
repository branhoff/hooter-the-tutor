#!/bin/bash

# Check python3 version
# if ! 3 -c 'import sys; assert sys.version_info >= (3,11)' > /dev/null; then
#     echo "python3 version should be >= 3.11"
#     exit 1
# fi

# Update python3 resources at the global level
python3 -m pip install --upgrade setuptools wheel pip

# Setup and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate the virtual environment."
    exit 1
fi

python3 -m pip install --upgrade setuptools wheel pip

# Check and install requirements
if [ -f "requires/requirements.txt" ]; then
    python3 -m pip install -r requires/requirements.txt
fi

if [ -f "requires/dev.txt" ]; then
    python3 -m pip install -r requires/dev.txt
fi
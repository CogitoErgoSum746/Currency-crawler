#!/bin/bash

# Update package lists
sudo apt update

# Install Python 3 pip
sudo apt install python3-pip python3-venv

# Check if pip is installed successfully
if pip --version &> /dev/null; then
    echo "pip is installed. Continuing with the rest of the commands..."
    # Create a virtual environment named 'env'
    python3 -m venv env

    # Activate the virtual environment
    source env/bin/activate

    # Install dependencies from requirements.txt
    pip install -r requirements.txt
else
    echo "pip is not installed. Exiting..."
    exit 1
fi
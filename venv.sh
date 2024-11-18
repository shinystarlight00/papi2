#!/bin/bash


apt install -y python3.10-venv python3-pip


# Define environment name
ENV_NAME=".venv"

# Check if the environment already exists
if [ -d "$ENV_NAME" ]; then
    echo "Virtual environment '$ENV_NAME' already exists. Activating..."
else
    echo "Creating virtual environment '$ENV_NAME'..."
    python3 -m venv "$ENV_NAME"
fi

# Activate the virtual environment
source "$ENV_NAME/bin/activate"

# Install packages if a requirements file is provided
if [ -f "requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "No requirements.txt file found. Skipping package installation."
fi

echo "Virtual environment '$ENV_NAME' is ready and activated."

# Keep the environment active in the shell
#exec "$SHELL"

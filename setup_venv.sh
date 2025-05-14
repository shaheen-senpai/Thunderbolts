#!/bin/bash

echo "Setting up Conda environment for intelligent chatbot project..."

# Environment name
ENV_NAME="chatbot_env"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Conda is not installed or not in PATH. Please install Conda first."
    exit 1
fi

# Create Conda environment if it doesn't exist
if ! conda info --envs | grep -q $ENV_NAME; then
    echo "Creating Conda environment '$ENV_NAME'..."
    conda create -y -n $ENV_NAME python=3.9
else
    echo "Conda environment '$ENV_NAME' already exists."
fi

# Activate Conda environment
echo "Activating Conda environment..."
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "Conda environment setup complete!"
echo "To activate the environment in the future, run: conda activate $ENV_NAME"
echo "To deactivate when done, run: conda deactivate"
echo ""

conda activate $ENV_NAME
echo "Current Conda environment: $(conda info --envs | grep '*' | awk '{print $1}')"
echo "Current Python version: $(python --version)"
echo "Current Python: $(which python)"
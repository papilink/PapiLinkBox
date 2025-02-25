#!/bin/bash

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
echo "Installing Python and dependencies..."
sudo apt install -y python3-pip python3-venv

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv myenv

# Install Python packages in the virtual environment
echo "Installing Python libraries..."
./myenv/bin/pip install --upgrade pip
./myenv/bin/pip install numpy pandas scikit-learn matplotlib jupyter
./myenv/bin/pip install tensorflow keras

# Add tensorflow-cpu alternative (uncomment if needed)
# ./myenv/bin/pip install tensorflow-cpu

echo -e "\n\033[32mEnvironment setup completed!\033[0m"
echo -e "To activate the virtual environment, run:"
echo -e "\033[1msource myenv/bin/activate\033[0m"
echo -e "To deactivate, run: \033[1mdeactivate\033[0m\n"

source myenv/bin/activate
python -c "import tensorflow as tf; print(tf.__version__)"
python -c "import pandas as pd; print(pd.__version__)"

#!/bin/bash

# ========================================
# Smart Image Generation - Installer
# ========================================

set -e  # Exit on any error

echo "========================================"
echo "Smart Image Generation Dependencies"
echo "========================================"

# Function to print colored output
print_status() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

# Check if Python3 is available
print_status "Checking Python3 installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check Python3 version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
print_status "Found Python3 version: $PYTHON_VERSION"

# Check if install_dependencies.py exists
print_status "Checking installation script..."
if [ ! -f "install_dependencies.py" ]; then
    print_error "install_dependencies.py not found"
    echo "Please ensure you're running this from the correct directory"
    exit 1
fi

# Check if script is executable
if [ ! -x "install_dependencies.py" ]; then
    print_status "Making install_dependencies.py executable..."
    chmod +x install_dependencies.py
fi

# Run the installation
print_status "Installing dependencies..."
if python3 install_dependencies.py; then
    print_success "Dependencies installed successfully!"
else
    print_error "Installation failed"
    echo "Please check the error messages above"
    exit 1
fi

# Make install.sh executable
print_status "Setting up permissions..."
chmod +x install.sh

# Installation completed
print_success "Installation completed successfully!"
echo "You can now run the Smart Image Generation system."

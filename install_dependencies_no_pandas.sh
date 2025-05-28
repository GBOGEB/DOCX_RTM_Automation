#!/bin/bash

# Script to install dependencies for DOCX_RTM_Automation_v1.0 without pandas

echo "Starting installation of dependencies..."

# Update package list
sudo apt-get update

# Install Python3 and pip
sudo apt-get install -y python3 python3-pip

# Install required Python libraries
pip3 install docx lxml

echo "Dependencies installed successfully!"
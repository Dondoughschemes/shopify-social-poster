#!/bin/bash
set -e

# Remove any old build artifacts
rm -rf lambda_build lambda.zip

# Create a build directory
mkdir lambda_build

# Install dependencies into the build directory
pip install -r lambda/requirements.txt -t lambda_build

# Copy the Lambda function code into the build directory
cp lambda_function.py lambda_build/

# Zip everything in the build directory
cd lambda_build
zip -r ../lambda.zip .
cd ..

# Clean up build directory (optional)
rm -rf lambda_build

echo "Lambda deployment package (lambda.zip) created successfully." 
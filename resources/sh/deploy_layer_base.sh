#!/bin/bash

# Define global variables
FUNCTION_NAME="base_layer"
BASE_PATH=".lambda/lambda_layers"
PYTHON_VERSION="python3.10"
AWS_REGION="sa-east-1"

# Define the required directory path
REQUIRED_DIR="/home/marcello/Documents/denethor"

# Validate the current working directory
if [ "$(pwd)" != "$REQUIRED_DIR" ]; then
  echo "Error: Script must be run from $REQUIRED_DIR"
  exit 1
fi

# Remove existing lambda layer directory
rm -Rf $BASE_PATH/$FUNCTION_NAME

# Create necessary directories
mkdir -p $BASE_PATH/$FUNCTION_NAME/python

# Install Python dependencies
python3 -m pip install --python-version $PYTHON_VERSION --only-binary=:all: --target $BASE_PATH/$FUNCTION_NAME/python -r requirements_aws.txt

# Copy additional resources
cp -R resources/libs/clustalw-2.1-linux $BASE_PATH/$FUNCTION_NAME/python

# Change to the lambda layer directory
cd $BASE_PATH/$FUNCTION_NAME

# Zip the lambda layer
zip -r ${FUNCTION_NAME}.zip python

# Publish the lambda layer to AWS
aws lambda publish-layer-version --layer-name $FUNCTION_NAME --zip-file fileb://${FUNCTION_NAME}.zip --compatible-runtimes $PYTHON_VERSION --region $AWS_REGION

# Return to the original directory
cd ../../..
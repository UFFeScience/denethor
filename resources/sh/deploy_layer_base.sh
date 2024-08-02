#!/bin/bash

# Define global variables
DENETHOR_DIR="/home/marcello/Documents/denethor"
LAYER_NAME="base_layer"
BASE_PATH=".lambda/lambda_layers"
PYTHON_VERSION="3.10"
PYTHON_RUNTIME="python$PYTHON_VERSION"
AWS_REGION="sa-east-1"

# Store the current working directory
ORIGINAL_DIR=$(pwd)

# Change to the required directory
cd $DENETHOR_DIR || { echo "Error: Cannot change to required directory $DENETHOR_DIR"; exit 1; }

# Remove existing lambda layer directory
rm -Rf $BASE_PATH/$LAYER_NAME

# Create necessary directories
mkdir -p $BASE_PATH/$LAYER_NAME/python

# Install Python dependencies
python3 -m pip install --python-version $PYTHON_VERSION --only-binary=:all: --target $BASE_PATH/$LAYER_NAME/python -r requirements_aws.txt

# Copy additional resources
cp -R resources/libs/clustalw-2.1-linux $BASE_PATH/$LAYER_NAME/python

# Change to the lambda layer directory
cd $BASE_PATH/$LAYER_NAME

# Zip the lambda layer
zip -r ${LAYER_NAME}.zip python

# Publish the lambda layer to AWS
aws lambda publish-layer-version --layer-name $LAYER_NAME --zip-file fileb://${LAYER_NAME}.zip --compatible-runtimes $PYTHON_RUNTIME --region $AWS_REGION

# Return to the original directory
# cd ../../..
cd $ORIGINAL_DIR
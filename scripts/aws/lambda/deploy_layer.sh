#!/bin/bash

# Load environment variables
source ../load_env_vars.sh

# Define global variables
DENETHOR_DIR="/home/marcello/Documents/denethor"

# Store the current working directory
ORIGINAL_DIR=$(pwd)

BASE_PATH=".tmp/lambda"
PYTHON_VERSION="3.10"
PYTHON_RUNTIME="python$PYTHON_VERSION"

# Define a map for additional resources
declare -A ADDITIONAL_RESOURCES_MAP
ADDITIONAL_RESOURCES_MAP["base_layer"]="resources/libs/clustalw-2.1-linux"
ADDITIONAL_RESOURCES_MAP["denethor_layer"]="src/denethor"

# Function to deploy a layer
deploy_layer() {
    local LAYER_NAME=$1
    local REQUIREMENTS_FILE=$2
    local ADDITIONAL_RESOURCES=${ADDITIONAL_RESOURCES_MAP[$LAYER_NAME]}

    # Change to the required directory
    cd $DENETHOR_DIR || { echo "Error: Cannot change to required directory $DENETHOR_DIR"; exit 1; }

    # Remove existing lambda layer directory
    rm -Rf $BASE_PATH/$LAYER_NAME/

    # Create necessary directories
    mkdir -p $BASE_PATH/$LAYER_NAME/python

    # Install Python dependencies if a requirements file is provided
    if [ -n "$REQUIREMENTS_FILE" ]; then
        python3 -m pip install --python-version $PYTHON_VERSION --only-binary=:all: --target $BASE_PATH/$LAYER_NAME/python -r $REQUIREMENTS_FILE
    fi

    # Copy additional resources
    cp -R $ADDITIONAL_RESOURCES $BASE_PATH/$LAYER_NAME/python

    # Change to the lambda layer directory
    cd $BASE_PATH/$LAYER_NAME

    # Zip the lambda layer
    zip -r ${LAYER_NAME}.zip python

    # Publish the lambda layer to AWS
    aws lambda publish-layer-version --layer-name $LAYER_NAME --zip-file fileb://${LAYER_NAME}.zip --compatible-runtimes $PYTHON_RUNTIME --region $aws_region

    # Return to the original directory
    cd $ORIGINAL_DIR
}

# Menu options
echo "Select the layer to deploy:"
echo "1) base_layer"
echo "2) denethor_layer"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        deploy_layer "base_layer" "requirements_aws.txt"
        ;;
    2)
        deploy_layer "denethor_layer" ""
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

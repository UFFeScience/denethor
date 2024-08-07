#!/bin/bash

# Define global variables
DENETHOR_DIR="/home/marcello/Documents/denethor"
AWS_ACCOUNT_ID="058264090960"
PYTHON_VERSION="3.10"
PYTHON_RUNTIME="python$PYTHON_VERSION"
AWS_REGION="sa-east-1"
IAM_ROLE="Lambda_S3_access_role"

BASE_LAYER_NAME="base_layer"
BASE_LAYER_VERSION="4"
DENETHOR_LAYER_NAME="denethor_layer"
DENETHOR_LAYER_VERSION="3"

BASE_LAYER="arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:layer:$BASE_LAYER_NAME:$BASE_LAYER_VERSION"
DENETHOR_LAYER="arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:layer:$DENETHOR_LAYER_NAME:$DENETHOR_LAYER_VERSION"

LAYERS="$BASE_LAYER $DENETHOR_LAYER"

# Function to display the menu and get the user's choice for function name
function choose_function_name() {
  echo "Please choose the function name for deployment:"
  echo "1. tree_constructor"
  echo "2. subtree_constructor"
  echo "3. maf_database_creator"
  echo "4. maf_database_aggregator"
  read -p "Enter the number corresponding to your choice: " choice

  case $choice in
    1) FUNCTION_NAME="tree_constructor"; DEFAULT_TIMEOUT=30; DEFAULT_MEMORY_SIZE=128 ;;
    2) FUNCTION_NAME="subtree_constructor"; DEFAULT_TIMEOUT=45; DEFAULT_MEMORY_SIZE=256 ;;
    3) FUNCTION_NAME="maf_database_creator"; DEFAULT_TIMEOUT=300; DEFAULT_MEMORY_SIZE=512 ;;
    4) FUNCTION_NAME="maf_database_aggregator"; DEFAULT_TIMEOUT=30; DEFAULT_MEMORY_SIZE=128 ;;
    *) echo "Invalid choice. Exiting."; exit 1 ;;
  esac
}

# Function to get the timeout value from the user
function choose_timeout() {
  read -p "Enter the timeout value (default is $DEFAULT_TIMEOUT): " timeout
  TIMEOUT=${timeout:-$DEFAULT_TIMEOUT}
}

# Function to get the memory size from the user
function choose_memory_size() {
  read -p "Enter the memory size (default is $DEFAULT_MEMORY_SIZE): " memory_size
  MEMORY_SIZE=${memory_size:-$DEFAULT_MEMORY_SIZE}
}

# Call the functions to get user inputs
choose_function_name
choose_timeout
choose_memory_size

# Store the current working directory
ORIGINAL_DIR=$(pwd)

# Change to the required directory
cd $DENETHOR_DIR || { echo "Error: Cannot change to required directory $DENETHOR_DIR"; exit 1; }

# Remove existing lambda function directory and recreate it
rm -Rf .lambda/lambda_functions/$FUNCTION_NAME/
mkdir -p .lambda/lambda_functions/$FUNCTION_NAME/

# Copy lambda function files
cp -R src/lambda_functions/${FUNCTION_NAME}* .lambda/lambda_functions/$FUNCTION_NAME/

# Change to the lambda function directory
cd .lambda/lambda_functions/$FUNCTION_NAME/

# Zip the lambda function
zip ${FUNCTION_NAME}.zip *


# Check if the function already exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION > /dev/null 2>&1; then
  echo "Function $FUNCTION_NAME already exists!"
  
  echo "Updating the function code..."
  aws lambda update-function-code --function-name $FUNCTION_NAME --zip-file fileb://${FUNCTION_NAME}.zip --region $AWS_REGION
  
  # Sleep for a few seconds to ensure the update-function-code operation completes
  echo "Sleeping for 5 seconds..."
  sleep 5
  
  echo "Updating the function configuration..."
  aws lambda update-function-configuration --function-name $FUNCTION_NAME --layers $LAYERS --timeout $TIMEOUT --memory-size $MEMORY_SIZE --region $AWS_REGION

else
  # Create the lambda function on AWS
  echo "Function $FUNCTION_NAME does not exist. Creating the function."
  aws lambda create-function --function-name $FUNCTION_NAME \
  --zip-file fileb://${FUNCTION_NAME}.zip \
  --handler ${FUNCTION_NAME}.handler \
  --runtime $PYTHON_RUNTIME \
  --role arn:aws:iam::$AWS_ACCOUNT_ID:role/service-role/$IAM_ROLE \
  --timeout $TIMEOUT \
  --memory-size $MEMORY_SIZE \
  --region $AWS_REGION \
  --layers $LAYERS
fi

# Return to the original directory
# cd ../../..
cd $ORIGINAL_DIR

# End of script
echo "Deployment completed successfully!"
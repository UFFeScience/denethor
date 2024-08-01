#!/bin/bash

# Define global variables
REQUIRED_DIR="/home/marcello/Documents/denethor"
AWS_ACCOUNT_ID="058264090960"
LAMBDA_LAYER_VERSION="6"
DENETHOR_LAYER_VERSION="2"
PYTHON_VERSION="python3.10"
AWS_REGION="sa-east-1"
IAM_ROLE="Lambda_S3_access_role"

# Function to display the menu and get the user's choice for function name
function choose_function_name() {
  echo "Please choose the function name for deployment:"
  echo "1. tree_constructor"
  echo "2. subtree_constructor"
  echo "3. maf_database_creator"
  echo "4. maf_database_aggregator"
  read -p "Enter the number corresponding to your choice: " choice

  case $choice in
    1) FUNCTION_NAME="tree_constructor"; DEFAULT_TIMEOUT=15; DEFAULT_MEMORY_SIZE=128 ;;
    2) FUNCTION_NAME="subtree_constructor"; DEFAULT_TIMEOUT=45; DEFAULT_MEMORY_SIZE=256 ;;
    3) FUNCTION_NAME="maf_database_creator"; DEFAULT_TIMEOUT=300; DEFAULT_MEMORY_SIZE=512 ;;
    4) FUNCTION_NAME="maf_database_aggregator"; DEFAULT_TIMEOUT=15; DEFAULT_MEMORY_SIZE=128 ;;
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

# Validate the current working directory
if [ "$(pwd)" != "$REQUIRED_DIR" ]; then
  echo "Error: Script must be run from $REQUIRED_DIR"
  exit 1
fi

# Remove existing lambda function directory
rm -Rf .lambda/lambda_functions/$FUNCTION_NAME/

# Create necessary directories
mkdir -p .lambda/lambda_functions/$FUNCTION_NAME/

# Copy lambda function files
cp -R src/lambda_functions/${FUNCTION_NAME}* .lambda/lambda_functions/$FUNCTION_NAME/

# Change to the lambda function directory
cd .lambda/lambda_functions/$FUNCTION_NAME/

# Zip the lambda function
zip ${FUNCTION_NAME}.zip *

# Create the lambda function on AWS
aws lambda create-function --function-name $FUNCTION_NAME \
--zip-file fileb://${FUNCTION_NAME}.zip \
--handler ${FUNCTION_NAME}.handler \
--runtime $PYTHON_VERSION \
--role arn:aws:iam::$AWS_ACCOUNT_ID:role/service-role/$IAM_ROLE \
--timeout $TIMEOUT \
--memory-size $MEMORY_SIZE \
--region $AWS_REGION \
--layers "arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:layer:lambda_layer:$LAMBDA_LAYER_VERSION" "arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:layer:denethor_layer:$DENETHOR_LAYER_VERSION"

# Return to the original directory
cd ../../..
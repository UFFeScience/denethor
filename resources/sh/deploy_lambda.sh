#!/bin/bash

# Define global variables
DENETHOR_DIR="/home/marcello/Documents/denethor"
AWS_ACCOUNT_ID="058264090960"
PYTHON_VERSION="3.10"
PYTHON_RUNTIME="python$PYTHON_VERSION"
AWS_REGION="sa-east-1"
IAM_ROLE="Lambda_S3_access_role"

BASE_LAYER_NAME="base_layer"
DENETHOR_LAYER_NAME="denethor_layer"

# Função para obter a versão mais recente de uma camada
get_latest_layer_version() {
  local layer_name=$1
  aws lambda list-layer-versions --layer-name "$layer_name" --query 'LayerVersions[0].Version' --output text
}

# Recuperar a versão mais recente das camadas
BASE_LAYER_VERSION=$(get_latest_layer_version "$BASE_LAYER_NAME")
DENETHOR_LAYER_VERSION=$(get_latest_layer_version "$DENETHOR_LAYER_NAME")

# Exibir as versões recuperadas
echo "Base Layer Version: $BASE_LAYER_VERSION"
echo "Denethor Layer Version: $DENETHOR_LAYER_VERSION"

BASE_LAYER="arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:layer:$BASE_LAYER_NAME:$BASE_LAYER_VERSION"
DENETHOR_LAYER="arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:layer:$DENETHOR_LAYER_NAME:$DENETHOR_LAYER_VERSION"

LAYERS="$BASE_LAYER $DENETHOR_LAYER"



# Function to display script usage
usage() {
    echo "Usage: $0 -f function_name -t timeout -m memory_size"
    echo "  -f function_name: tree_constructor, subtree_constructor, maf_database_creator, maf_database_aggregator"
    echo "  -t timeout: integer between 30 and 300"
    echo "  -m memory_size: integer between 128 and 2048"
    exit 1
}

# Function to validate function_name
validate_function_name() {
    if [[ ! "$1" =~ ^(tree_constructor|subtree_constructor|maf_database_creator|maf_database_aggregator)$ ]]; then
        echo "Invalid function_name: $1"
        usage
    fi
}

# Function to validate timeout
validate_timeout() {
    if [[ ! "$1" =~ ^[0-9]+$ ]] || [ "$1" -lt 30 ] || [ "$1" -gt 300 ]; then
        echo "Invalid timeout: $1"
        usage
    fi
}

# Function to validate memory_size
validate_memory_size() {
    if [[ ! "$1" =~ ^[0-9]+$ ]] || [ "$1" -lt 128 ] || [ "$1" -gt 2048 ]; then
        echo "Invalid memory_size: $1"
        usage
    fi
}

# Reading command line parameters
while getopts ":f:t:m:" opt; do
  case $opt in
    f)
      FUNCTION_NAME=$OPTARG
      ;;
    t)
      TIMEOUT=$OPTARG
      ;;
    m)
      MEMORY_SIZE=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      usage
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      usage
      ;;
  esac
done


# Validate parameters
validate_function_name "$FUNCTION_NAME"
validate_timeout "$TIMEOUT"
validate_memory_size "$MEMORY_SIZE"

echo "Deploying function: $FUNCTION_NAME"
echo "Timeout: $TIMEOUT"
echo "Memory size: $MEMORY_SIZE"

exit 1

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
  echo "Sleeping for 2 seconds..."
  sleep 2
  
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
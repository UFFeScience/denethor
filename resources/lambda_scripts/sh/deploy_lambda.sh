#!/bin/bash

##################################################################################

# Script to deploy a lambda function to AWS based on the function name, timeout, 
# memory size and append_memory flag provided as command line parameters.

# If append_memory is true, the memory size is appended to the function name,
# indicating the memory size used by the function, i.e., "configuration"

# The script uses the latest versrions of the 'base' and 'denethor' layers.

##################################################################################




##################################################################################

# Script usage and parameter validation functions

##################################################################################

# Function to display script usage
usage() {
    echo "Usage: $0 -f function_name -t timeout -m memory_size [-a append_memory]"
    echo "  -f function_name: tree_constructor, subtree_constructor, maf_database_creator, maf_database_aggregator"
    echo "  -t timeout: integer between 30 and 300"
    echo "  -m memory_size: integer between 128 and 2048"
    echo "  -a append_memory: boolean to append memory size to function name"
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
append_memory=false
while getopts ":f:t:m:a:" opt; do
  case $opt in
    f)
      function_name=$OPTARG
      ;;
    t)
      timeout=$OPTARG
      ;;
    m)
      memory_size=$OPTARG
      ;;
    a)
      append_memory=$OPTARG
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
validate_function_name "$function_name"
validate_timeout "$timeout"
validate_memory_size "$memory_size"

echo "Deploying function: $function_name"
echo "Timeout: $timeout"
echo "Memory size: $memory_size"
echo "Append memory to function name: $append_memory"

##################################################################################
##################################################################################





##################################################################################

# Deployment script of the lambda function

##################################################################################

# Define global variables
DENETHOR_DIR="/home/marcello/Documents/denethor"
AWS_ACCOUNT_ID="058264090960"
PYTHON_VERSION="3.10"
PYTHON_RUNTIME="python$PYTHON_VERSION"
AWS_REGION="sa-east-1"
IAM_ROLE="Lambda_S3_access_role"

BASE_LAYER_NAME="base_layer"
DENETHOR_LAYER_NAME="denethor_layer"

# Get the latest version of the layer
get_latest_layer_version() {
  local layer_name=$1
  aws lambda list-layer-versions --layer-name "$layer_name" --query 'LayerVersions[0].Version' --output text
}

# Define the layers with the latest versions
BASE_LAYER_VERSION=$(get_latest_layer_version "$BASE_LAYER_NAME")
DENETHOR_LAYER_VERSION=$(get_latest_layer_version "$DENETHOR_LAYER_NAME")

echo "Base Layer Version: $BASE_LAYER_VERSION"
echo "Denethor Layer Version: $DENETHOR_LAYER_VERSION"

BASE_LAYER="arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:layer:$BASE_LAYER_NAME:$BASE_LAYER_VERSION"
DENETHOR_LAYER="arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:layer:$DENETHOR_LAYER_NAME:$DENETHOR_LAYER_VERSION"

LAYERS="$BASE_LAYER $DENETHOR_LAYER"


# Define additional dependency files for each function
declare -A dependencies
dependencies["tree_constructor"]=""
dependencies["subtree_constructor"]=""
dependencies["maf_database_creator"]=""
dependencies["maf_database_aggregator"]="maf_database_creator_core.py"

# Store the current working directory
ORIGINAL_DIR=$(pwd)

# Change to the required directory
cd $DENETHOR_DIR || { echo "Error: Cannot change to required directory $DENETHOR_DIR"; exit 1; }

# Remove existing lambda function directory and recreate it
rm -Rf .lambda/lambda_functions/$function_name/
mkdir -p .lambda/lambda_functions/$function_name/

# Copy lambda function files
cp -R src/lambda_functions/${function_name}* .lambda/lambda_functions/$function_name/ || { echo "Error: Cannot copy $function_name files"; exit 1; }

# Copy additional dependency files if any
for dep in ${dependencies[$function_name]}; do
  cp src/lambda_functions/$dep .lambda/lambda_functions/$function_name/ || { echo "Error: Cannot copy dependency file $dep"; exit 1; }
done

# Change to the lambda function directory
cd .lambda/lambda_functions/$function_name/

# Zip the lambda function
zip ${function_name}.zip * || { echo "Error: Cannot zip lambda function"; exit 1; }



# Append memory size to the function name if append_memory is true
if [ "$append_memory" = true ]; then
  function_name_aws="${function_name}_${memory_size}"
else
  function_name_aws="$function_name"
fi


# Check if the function already exists
function_exists=$( \
  aws lambda list-functions \
  --query "Functions[?FunctionName=='$function_name_aws'].FunctionName" \
  --region $AWS_REGION \
  --output text)

if [ "$function_exists" = "$function_name_aws" ]; then
  
  echo -e "\nFunction $function_name_aws already exists!"
  
  echo -e "\nUpdating the $function_name_aws function code..."
  aws lambda update-function-code \
  --function-name $function_name_aws \
  --zip-file fileb://${function_name}.zip \
  --region $AWS_REGION
  
  # Sleep for a few seconds to ensure the update-function-code operation completes
  echo -e "\nSleeping for a few seconds..."
  sleep 2
  
  echo "Updating the $function_name_aws function configuration..."
  aws lambda update-function-configuration \
  --function-name $function_name_aws \
  --layers $LAYERS \
  --timeout $timeout \
  --memory-size $memory_size \
  --region $AWS_REGION \
  || { echo -e "\n>>>> ERROR: Cannot update $function_name_aws function configuration.\n"; exit 1; }

else
  # Create the lambda function on AWS
  echo -e "\n Function $function_name_aws does not exist. Creating the function."
  aws lambda create-function \
  --function-name $function_name_aws \
  --zip-file fileb://${function_name}.zip \
  --handler ${function_name}.handler \
  --runtime $PYTHON_RUNTIME \
  --role arn:aws:iam::$AWS_ACCOUNT_ID:role/service-role/$IAM_ROLE \
  --timeout $timeout \
  --memory-size $memory_size \
  --region $AWS_REGION \
  --layers $LAYERS \
  || { echo -e "\n>>>> ERROR: Cannot create $function_name_aws function.\n"; exit 1; }
fi

# Return to the original directory
# cd ../../..
cd $ORIGINAL_DIR

# End of script
echo -e "\n-------------------------------------------------------------------------------\n"
echo -e "Deployment completed successfully for function $function_name_aws!"
echo -e "\n-------------------------------------------------------------------------------\n"
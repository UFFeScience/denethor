#!/bin/bash

##################################################################################

# Script to deploy a lambda function to AWS based on command line parameters:
# - function name
# - timeout
# - memory size
# - append_memory flag
#
# If append_memory is true, the memory size is appended to the function name,
# indicating the memory size used by the function, i.e., "configuration"

# The script uses the latest versions of the 'base' and 'denethor' layers.

##################################################################################


# Load environment variables
source ../load_env_vars.sh

##################################################################################

# Script usage and parameter validation functions

##################################################################################

# Function to display script usage
usage() {
    echo "Usage: $0 -f function_name -t timeout -m memory_size [-a append_memory]"
    echo "  -f function_name: ${lambda_function_names[@]}"
    echo "  -t timeout: integer between 30 and 300"
    echo "  -m memory_size: ${lambda_memory_sizes[@]}"
    echo "  -a append_memory: boolean to append memory size to function name"
    exit 1
}

# Function to validate function_name
validate_function_name() {
    if [[ ! " ${lambda_function_names[*]} " =~ " $1 " ]]; then
        echo "Invalid function_name: $1" >&2
        usage
    fi
}

# Function to validate timeout
validate_timeout() {
    if [[ ! "$1" =~ ^[0-9]+$ ]] || [ "$1" -lt 30 ] || [ "$1" -gt 300 ]; then
        echo "Invalid timeout: $1" >&2
        usage
    fi
}

# Function to validate memory_size
validate_memory_size() {
    if [[ ! " ${lambda_memory_sizes[*]} " =~ " $1 " ]]; then
        echo "Invalid memory_size: $1" >&2
        usage
    fi
}

# Reading command line parameters
APPEND_MEMORY=false
while getopts ":f:t:m:a:" opt; do
  case $opt in
    f) FUNCTION_NAME=$OPTARG ;;
    t) TIMEOUT=$OPTARG ;;
    m) MEMORY_SIZE=$OPTARG ;;
    a) APPEND_MEMORY=$OPTARG ;;
    *)
      echo "Invalid option or missing argument." >&2
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
echo "Append memory to function name: $APPEND_MEMORY"

##################################################################################
##################################################################################





##################################################################################

# Deployment script of the lambda function

##################################################################################

# Define global variables
SLEEP_DURATION=10

DENETHOR_DIR="/home/marcello/Documents/denethor"
PYTHON_VERSION="3.10"
PYTHON_RUNTIME="python$PYTHON_VERSION"

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

BASE_LAYER="arn:aws:lambda:$aws_region:$aws_account_id:layer:$BASE_LAYER_NAME:$BASE_LAYER_VERSION"
DENETHOR_LAYER="arn:aws:lambda:$aws_region:$aws_account_id:layer:$DENETHOR_LAYER_NAME:$DENETHOR_LAYER_VERSION"

LAYERS="$BASE_LAYER $DENETHOR_LAYER"


# Define additional dependency files for each function
declare -A dependencies
dependencies["tree_constructor"]=""
dependencies["subtree_constructor"]=""
dependencies["maf_database_creator"]=""
dependencies["maf_database_aggregator"]="maf_database_creator_core.py"

# Store the current working directory
ORIGINAL_DIR=$(pwd)

cd $DENETHOR_DIR || { echo "Error: Cannot change to required directory $DENETHOR_DIR" >&2; exit 1; }
cd $DENETHOR_DIR || { echo "Error: Cannot change to required directory $DENETHOR_DIR"; exit 1; }

rm -Rf .tmp/lambda/$function_name/
mkdir -p .tmp/lambda/$function_name/

# Copy lambda function files
cp -R src/lambda/${function_name}* .tmp/lambda/$function_name/ || { echo "Error: Cannot copy $function_name files" >&2; exit 1; }

# Copy additional dependency files if any
for dep in ${dependencies[$function_name]}; do
  cp src/lambda/$dep .tmp/lambda/$function_name/ || { echo "Error: Cannot copy dependency file $dep" >&2; exit 1; }
done
done
# Change to the lambda function directory
cd .tmp/lambda/$function_name/

# Zip the lambda function
zip ${function_name}.zip * || { echo "Error: Cannot zip lambda function" >&2; exit 1; }
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
  
  echo -e "\n>>>>Function $function_name_aws already exists! Updating the function code..."

  aws lambda update-function-code \
  --function-name $function_name_aws \
  --zip-file fileb://${function_name}.zip \
  --region $AWS_REGION \
  || { echo -e "\n>>>> ERROR: Cannot update $function_name_aws function code.\n"; exit 1; }

  
  echo -e "\n>>>>Updating the $function_name_aws function configuration..."
  
  # Sleep for a few seconds to ensure the update-function-code operation completes
  echo -e "\n>>>>Waiting $SLEEP_DURATION seconds to ensure the update-function-code operation completes"
  sleep $SLEEP_DURATION

  aws lambda update-function-configuration \
  --function-name $function_name_aws \
  --layers $LAYERS \
  --timeout $timeout \
  --memory-size $memory_size \
  --region $AWS_REGION \
  || { echo -e "\n>>>> ERROR: Cannot update $function_name_aws function configuration.\n"; exit 1; }

else
  # Create the lambda function on AWS
  echo -e "\n>>>>Function $function_name_aws does not exist. Creating the function."
  
  aws lambda create-function \
  --function-name $function_name_aws \
  --zip-file fileb://${function_name}.zip \
  --handler ${function_name}.handler \
  --runtime $PYTHON_RUNTIME \
  --role arn:aws:iam::$aws_account_id:role/service-role/$lambda_role \
  --timeout $timeout \
  --memory-size $memory_size \
  --region $aws_region \
  --layers $LAYERS \
  || { echo -e "\n>>>> ERROR: Cannot create $function_name_aws function.\n"; exit 1; }
fi

# Return to the original directory
cd $ORIGINAL_DIR

# End of script
echo -e "\n-----------------------------------------------------------------------------------------------\n"
echo -e "Deployment completed successfully for function $function_name_aws! with memory size $memory_size"
echo -e "\n-----------------------------------------------------------------------------------------------\n"
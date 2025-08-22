#!/bin/bash

##################################################################################

# Script to deploy a lambda function to AWS based on command line parameters:
# - function_name
# - timeout
# - memory_size
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
    echo "  -f function_name: ${LAMBDA_FUNCTION_NAMES[@]}"
    echo "  -t timeout: integer between 30 and 300"
    echo "  -m memory_size: ${LAMBDA_MEMORY_SIZES[@]}"
    echo "  -a append_memory: boolean to append memory size to function name"
    exit 1
}

# Function to validate function_name
validate_function_name() {
    if [[ ! " ${LAMBDA_FUNCTION_NAMES[*]} " =~ " $1 " ]]; then
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
    if [[ ! " ${LAMBDA_MEMORY_SIZES[*]} " =~ " $1 " ]]; then
        echo "Invalid memory_size: $1" >&2
        usage
    fi
}

# Reading command line parameters
append_memory=false
while getopts ":f:t:m:a:" opt; do
  case $opt in
    f) function_name=$OPTARG ;;
    t) timeout=$OPTARG ;;
    m) memory_size=$OPTARG ;;
    a) append_memory=$OPTARG ;;
    *)
      echo "Invalid option or missing argument." >&2
      usage
      ;;
  esac
done

append_memory=$(echo "$append_memory" | tr '[:upper:]' '[:lower:]')

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

# Get the latest version of the layer
get_latest_layer_version() {
  local layer_name=$1
  aws lambda list-layer-versions --layer-name "$layer_name" --query 'LayerVersions[0].Version' --output text
}

# Define the layers with the latest versions
base_layer_version=$(get_latest_layer_version "$BASE_LAYER_NAME")
denethor_layer_version=$(get_latest_layer_version "$DENETHOR_LAYER_NAME")

echo "Base Layer Version: $base_layer_version"
echo "Denethor Layer Version: $denethor_layer_version"

base_layer="arn:aws:lambda:$aws_region:$aws_account_id:layer:$BASE_LAYER_NAME:$base_layer_version"
denethor_layer="arn:aws:lambda:$aws_region:$aws_account_id:layer:$DENETHOR_LAYER_NAME:$denethor_layer_version"

layers="$base_layer $denethor_layer"


# Define additional dependency files for each function
declare -A dependencies
dependencies["tree_constructor"]=""
dependencies["subtree_constructor"]=""
dependencies["maf_database_creator"]=""
dependencies["maf_database_aggregator"]="maf_database_creator_core.py"

# Store the current working directory
original_dir=$(pwd)

cd $DENETHOR_PATH || { echo "Error: Cannot change to required directory $DENETHOR_PATH" >&2; exit 1; }

rm -Rf .tmp/lambda/$function_name/
mkdir -p .tmp/lambda/$function_name/

# Copy lambda function files
cp -R src/lambda/${function_name}* .tmp/lambda/$function_name/ || { echo "Error: Cannot copy $function_name files" >&2; exit 1; }

# Copy additional dependency files if any
for dep in ${dependencies[$function_name]}; do
  cp src/lambda/$dep .tmp/lambda/$function_name/ || { echo "Error: Cannot copy dependency file $dep" >&2; exit 1; }
done

# Change to the lambda function directory
cd .tmp/lambda/$function_name/

# Zip the lambda function
zip "${function_name}.zip" ./* || { echo "Error: Cannot zip lambda function" >&2; exit 1; }

# Append memory size to the function name if append_memory is true
if [ "$append_memory" = true ]; then
  function_name_final="${function_name}_${memory_size}"
else
  function_name_final="$function_name"
fi


# Check if the function already exists
function_exists=$( \
  aws lambda list-functions \
  --query "Functions[?FunctionName=='$function_name_final'].FunctionName" \
  --region $AWS_REGION \
  --output text)

if [ "$function_exists" = "$function_name_final" ]; then

  echo -e "\n>>>>Function $function_name_final already exists! Updating the function code..."

  # aws lambda update-function-code \
  # --function-name $function_name_final \
  # --zip-file fileb://${function_name}.zip \
  # --region $AWS_REGION \
  # || { echo -e "\n>>>> ERROR: Cannot update $function_name_final function code.\n"; exit 1; }


  echo -e "\n>>>>Updating the $function_name_final function configuration..."

  # Sleep for a few seconds to ensure the update-function-code operation completes
  echo -e "\n>>>>Waiting $SLEEP_DURATION seconds to ensure the update-function-code operation completes"
  sleep $SLEEP_DURATION

  # aws lambda update-function-configuration \
  # --function-name $function_name_final \
  # --layers $layers \
  # --timeout $timeout \
  # --memory-size $memory_size \
  # --region $AWS_REGION \
  # || { echo -e "\n>>>> ERROR: Cannot update $function_name_final function configuration.\n"; exit 1; }

else
  # Create the lambda function on AWS
  echo -e "\n>>>>Function $function_name_final does not exist. Creating the function."

  # aws lambda create-function \
  # --function-name $function_name_final \
  # --zip-file fileb://${function_name}.zip \
  # --handler ${function_name}.handler \
  # --runtime $PYTHON_RUNTIME \
  # --role arn:aws:iam::$AWS_ACCOUNT_ID:role/service-role/$LAMBDA_S3_ACCESS_ROLE \
  # --timeout $timeout \
  # --memory-size $memory_size \
  # --region $AWS_REGION \
  # --layers $layers \
  # || { echo -e "\n>>>> ERROR: Cannot create $function_name_final function.\n"; exit 1; }
fi

# Return to the original directory
cd $original_dir

# End of script
echo -e "\n-----------------------------------------------------------------------------------------------\n"
echo -e "Deployment completed successfully for function $function_name_final! with memory size $memory_size and timeout $timeout seconds."
echo -e "\n-----------------------------------------------------------------------------------------------\n"
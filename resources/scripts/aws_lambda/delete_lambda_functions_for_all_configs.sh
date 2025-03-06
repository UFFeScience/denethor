#!/bin/bash

# List of memory sizes (configs)
memory_sizes=("128" "256" "512" "1024" "2048")

# List of function names
function_names=("tree_constructor" "subtree_constructor" "maf_database_creator" "maf_database_aggregator")

# AWS region
region="sa-east-1"

current_dir=$(dirname "$0")
echo -e "Deleting lambda functions for all configurations in region $region"
echo -e "Current directory: $current_dir"

# Iterate over function names
for function_name in "${function_names[@]}"; do
  
  for memory_size in "${memory_sizes[@]}"; do
    function_name_aws="${function_name}_${memory_size}"
    
    # Check if the function exists in AWS
    function_exists=$(aws lambda list-functions \
      --query "Functions[?FunctionName=='$function_name_aws'].FunctionName" \
      --region "$region" \
      --output text)
    
    if [ "$function_exists" == "$function_name_aws" ]; then
      "$current_dir"/delete_lambda_function.sh -f "$function_name_aws" -r "$region" -y || exit 1
    fi
  done
done
#!/bin/bash

# List of memory sizes
memory_sizes=(128 256 512 1024 2048)

# List of function names
function_names=("tree_constructor" "subtree_constructor" "maf_database_creator" "maf_database_aggregator")

# AWS region
region="sa-east-1"

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
      ./delete_lambda.sh -f "$function_name_aws" -r "$region" -y || exit 1
    fi
  done
done
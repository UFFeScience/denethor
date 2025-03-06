#!/bin/bash

# Array of memory sizes
memory_sizes=(128 256 512 1024 2048)


# Array of function names
function_names=("tree_constructor" "subtree_constructor" "maf_database_creator" "maf_database_aggregator")
#function_names=("tree_constructor")

# Associating timeouts to functions
declare -A timeouts
timeouts=( ["tree_constructor"]=30 ["subtree_constructor"]=30 ["maf_database_creator"]=120 ["maf_database_aggregator"]=30 )

# Variable to indicate appending memory size to function name
append_memory=true

current_dir=$(dirname "$0")
echo -e "Current directory: $current_dir"

echo -e "\n------------------------------------------------------------------------------------------------------\n"
echo -e " Starting deployment of: ${function_names[@]} using memory sizes: ${memory_sizes[@]} in region $region}"
echo -e "\n------------------------------------------------------------------------------------------------------\n"


# Iterate over each function name
for function_name in "${function_names[@]}"; do
  echo -e "\n>>>> Function name: $function_name\n"
  
  # Get the timeout for the current function
  timeout=${timeouts[$function_name]}
  
  # Iterate over each memory size
  for memory_size in "${memory_sizes[@]}"; do
    echo -e "\n>>>> Memory size: $memory_size\n"
    
    # Call deploy_lambda.sh with the current configuration
    ./deploy_lambda_function.sh -f "$function_name" -t "$timeout" -m "$memory_size" -a "$append_memory"
  
    # Check the exit code of the script
    if [ $? -ne 0 ]; then
      echo ">>>> ERROR: Deploy failed for function $function_name with memory size $memory_size. Exiting..."
      exit 1
    fi
  done
done
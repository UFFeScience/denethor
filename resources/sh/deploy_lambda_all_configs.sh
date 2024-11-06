#!/bin/bash

# Array of memory sizes
memory_sizes=(128 256 512 1024 2048)

# Array of function names
function_names=("tree_constructor" "subtree_constructor" "maf_database_creator" "maf_database_aggregator")

# Associating timeouts to functions
declare -A timeouts
timeouts=( ["tree_constructor"]=60 ["subtree_constructor"]=120 ["maf_database_creator"]=180 ["maf_database_aggregator"]=240 )

# Iterate over each memory size
for memory_size in "${memory_sizes[@]}"; do
  # Iterate over each function name
  for function_name in "${function_names[@]}"; do
    # Get the timeout for the current function
    timeout=${timeouts[$function_name]}
    
    # Call deploy_lambda.sh with the current configuration
    ./deploy_lambda.sh -f "$function_name" -t "$timeout" -m "$memory_size"
  done
done
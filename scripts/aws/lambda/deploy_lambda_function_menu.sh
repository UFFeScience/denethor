#!/bin/bash

# Load environment variables
source ../load_env_vars.sh

# Associating timeouts to functions
declare -A timeouts
timeouts=( ["tree_constructor"]=30 ["subtree_constructor"]=30 ["maf_database_creator"]=300 ["maf_database_aggregator"]=30 )


# Function to display the menu and get the user's choice for function name
function choose_function_name() {
  echo "Please choose the function name for deployment:"
  for i in "${!lambda_function_names[@]}"; do
    echo "$((i+1)). ${lambda_function_names[$i]}"
  done
  read -p "Enter the number corresponding to your choice: " choice

  case $choice in
    1) FUNCTION_NAME=${lambda_function_names[0]}; DEFAULT_TIMEOUT=30; DEFAULT_MEMORY_SIZE=256 ;;
    2) FUNCTION_NAME=${lambda_function_names[1]}; DEFAULT_TIMEOUT=45; DEFAULT_MEMORY_SIZE=512 ;;
    3) FUNCTION_NAME=${lambda_function_names[2]}; DEFAULT_TIMEOUT=300; DEFAULT_MEMORY_SIZE=1024 ;;
    4) FUNCTION_NAME=${lambda_function_names[3]}; DEFAULT_TIMEOUT=30; DEFAULT_MEMORY_SIZE=128 ;;
    *) echo "Invalid choice. Exiting."; exit 1 ;;
  esac
  echo "You chose: $FUNCTION_NAME"
}

# Function to get the deployment type from the user
function choose_deployment_type() {
  echo "Please choose the deployment type:"
  echo "1. Deploy one configuration"
  echo "2. Deploy all configurations"
  read -p "Enter your choice (1 or 2): " deployment_choice
  case $deployment_choice in
    1) DEPLOYMENT_TYPE="single" ;;
    2) DEPLOYMENT_TYPE="all" ;;
    *) echo "Invalid choice. Exiting."; exit 1 ;;
  esac
  echo "You chose: $DEPLOYMENT_TYPE"
}

# Function to get the timeout value from the user
function choose_timeout() {
  read -p "Enter the timeout value (default is $DEFAULT_TIMEOUT): " timeout
  TIMEOUT=${timeout:-$DEFAULT_TIMEOUT}
  echo "You chose: $TIMEOUT"
}

# Function to get the memory size from the user
function choose_memory_size() {
  read -p "Enter the memory size (default is $DEFAULT_MEMORY_SIZE): " memory_size
  MEMORY_SIZE=${memory_size:-$DEFAULT_MEMORY_SIZE}
  echo "You chose: $MEMORY_SIZE"
}

# Function to ask if the user wants to append memory size to the function name
function choose_append_memory() {
  read -p "Append memory size to function name? (y/n): " append_memory
  if [[ "$append_memory" =~ ^[Yy]$ ]]; then
    APPEND_MEMORY=true
  else
    APPEND_MEMORY=false
  fi
  echo "You chose: $APPEND_MEMORY"
}

# Call the functions to get user inputs
choose_function_name
choose_deployment_type

if [[ "$DEPLOYMENT_TYPE" == "single" ]]; then
  choose_timeout
  choose_memory_size
  choose_append_memory
  # Call the deploy_lambda.sh script with the user inputs
  ./deploy_lambda_function.sh -f $FUNCTION_NAME -t $TIMEOUT -m $MEMORY_SIZE -a $APPEND_MEMORY

else
  # For deploying all configurations
  # Get the timeout for the current function
  TIMEOUT=${timeouts[$FUNCTION_NAME]}
  APPEND_MEMORY=true

  # Iterate over each memory size
  for MEMORY_SIZE in "${lambda_memory_sizes[@]}"; do
    echo -e "\n>>>> Memory size: $MEMORY_SIZE\n"

    # Call deploy_lambda.sh with the current configuration
    ./deploy_lambda_function.sh -f "$FUNCTION_NAME" -t "$TIMEOUT" -m "$MEMORY_SIZE" -a "$APPEND_MEMORY"

    # Check the exit code of the script
    if [ $? -ne 0 ]; then
      echo ">>>> ERROR: Deploy failed for function $FUNCTION_NAME with memory size $MEMORY_SIZE. Exiting..."
      exit 1
    fi
  done
fi

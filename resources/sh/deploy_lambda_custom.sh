#!/bin/bash

# Function to display the menu and get the user's choice for function name
function choose_function_name() {
  echo "Please choose the function name for deployment:"
  echo "1. tree_constructor"
  echo "2. subtree_constructor"
  echo "3. maf_database_creator"
  echo "4. maf_database_aggregator"
  read -p "Enter the number corresponding to your choice: " choice

  # case $choice in
  #   1) FUNCTION_NAME="tree_constructor"; DEFAULT_TIMEOUT=30; DEFAULT_MEMORY_SIZE=128 ;;
  #   2) FUNCTION_NAME="subtree_constructor"; DEFAULT_TIMEOUT=45; DEFAULT_MEMORY_SIZE=256 ;;
  #   3) FUNCTION_NAME="maf_database_creator"; DEFAULT_TIMEOUT=300; DEFAULT_MEMORY_SIZE=512 ;;
  #   4) FUNCTION_NAME="maf_database_aggregator"; DEFAULT_TIMEOUT=30; DEFAULT_MEMORY_SIZE=128 ;;
  #   *) echo "Invalid choice. Exiting."; exit 1 ;;
  # esac
  case $choice in
    1) FUNCTION_NAME="tree_constructor"; DEFAULT_TIMEOUT=30; DEFAULT_MEMORY_SIZE=256 ;;
    2) FUNCTION_NAME="subtree_constructor"; DEFAULT_TIMEOUT=45; DEFAULT_MEMORY_SIZE=512 ;;
    3) FUNCTION_NAME="maf_database_creator"; DEFAULT_TIMEOUT=300; DEFAULT_MEMORY_SIZE=1024 ;;
    4) FUNCTION_NAME="maf_database_aggregator"; DEFAULT_TIMEOUT=30; DEFAULT_MEMORY_SIZE=128 ;;
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

# Function to ask if the user wants to append memory size to the function name
function choose_append_memory() {
  read -p "Append memory size to function name? (y/n): " append_memory
  if [[ "$append_memory" =~ ^[Yy]$ ]]; then
    APPEND_MEMORY=true
  else
    APPEND_MEMORY=false
  fi
}

# Call the functions to get user inputs
choose_function_name
choose_timeout
choose_memory_size
choose_append_memory

# Call the deploy_lambda.sh script with the user inputs
./deploy_lambda.sh -f $FUNCTION_NAME -t $TIMEOUT -m $MEMORY_SIZE -a $APPEND_MEMORY
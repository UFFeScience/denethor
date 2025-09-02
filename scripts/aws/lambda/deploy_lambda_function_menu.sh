#!/bin/bash

# Load environment variables
source ../load_env_vars.sh


# Parallel arrays for default timeout and memory (defined in .env)
# LAMBDA_FUNCTION_NAMES, LAMBDA_DEFAULT_TIMEOUTS, LAMBDA_DEFAULT_MEMORY

if [[ ${#LAMBDA_FUNCTION_NAMES[@]} -ne ${#LAMBDA_DEFAULT_TIMEOUTS[@]} || ${#LAMBDA_FUNCTION_NAMES[@]} -ne ${#LAMBDA_DEFAULT_MEMORY[@]} ]]; then
  echo "Array size mismatch in .env. Check LAMBDA_FUNCTION_NAMES, LAMBDA_DEFAULT_TIMEOUTS, and LAMBDA_DEFAULT_MEMORY."
  exit 1
fi

# Function to display the menu and get the user's choice for function name
function choose_function_name() {
  echo "Please choose the function name for deployment:"
  for i in "${!LAMBDA_FUNCTION_NAMES[@]}"; do
    echo "$((i+1)). ${LAMBDA_FUNCTION_NAMES[$i]}"
  done
  read -p "Enter the number corresponding to your choice: " choice

  # Validate the input
  if ! [[ "$choice" =~ ^[0-9]+$ ]]; then
    echo "Invalid input. Exiting."
    exit 1
  fi

  idx=$((choice-1))
  if [[ $idx -ge 0 && $idx -lt ${#LAMBDA_FUNCTION_NAMES[@]} ]]; then
    function_name=${LAMBDA_FUNCTION_NAMES[$idx]}
    default_timeout=${LAMBDA_DEFAULT_TIMEOUTS[$idx]}
    default_memory_size=${LAMBDA_DEFAULT_MEMORY[$idx]}
    echo ""
  else
    echo "Invalid choice. Exiting."
    exit 1
  fi
}

# Function to get the deployment type from the user
function choose_deployment_type() {
  read -p "Enter your choice [single or all] (default is single): " deployment_type
  deployment_type=${deployment_type:-"single"}
  if [[ "$deployment_type" != "single" && "$deployment_type" != "all" ]]; then
    echo "Invalid choice. Exiting."
    exit 1
  fi
  echo ""
}

function choose_region() {
  read -p "Enter the AWS region (default is $AWS_REGION): " region
  region=${region:-$AWS_REGION}
  echo ""
}

# Function to get the timeout value from the user
function choose_timeout() {
  read -p "Enter the timeout value (default is $default_timeout): " timeout
  timeout=${timeout:-$default_timeout}
  echo ""
}

# Function to get the memory size from the user
function choose_memory_size() {
  read -p "Enter the memory size (default is $default_memory_size): " memory_size
  memory_size=${memory_size:-$default_memory_size}
  echo ""
}

# Function to ask if the user wants to append memory size to the function name
function choose_append_memory() {
  read -p "Append memory size to function name? [y/n] (default is n): " append_memory
  if [[ $append_memory =~ ^[Yy]$ ]]; then
    append_memory=true
  else
    append_memory=false
  fi
  echo ""
}

# Call the functions to get user inputs
choose_function_name
choose_deployment_type

if [[ "$deployment_type" == "single" ]]; then
  choose_region
  choose_timeout
  choose_memory_size
  choose_append_memory
  # Call the deploy_lambda.sh script with the user inputs
  ./deploy_lambda_function.sh -f "$function_name" -r "$region" -t "$timeout" -m "$memory_size" -a "$append_memory"

else
  # For deploying all configurations
  # Get the index of the selected function
  idx=-1
  for i in "${!LAMBDA_FUNCTION_NAMES[@]}"; do
    if [[ "${LAMBDA_FUNCTION_NAMES[$i]}" == "$function_name" ]]; then
      idx=$i
      break
    fi
  done
  if [[ $idx -eq -1 ]]; then
    echo "Function name not found in LAMBDA_FUNCTION_NAMES. Exiting."
    exit 1
  fi
  region=$AWS_REGION
  timeout=${LAMBDA_DEFAULT_TIMEOUTS[$idx]}
  append_memory=true

  # Itera sobre cada memória
  for memory_size in "${LAMBDA_MEMORY_SIZES[@]}"; do
    echo -e "\n>>>> Memory size: $memory_size\n"

    # Chama o deploy com a configuração atual
    ./deploy_lambda_function.sh -f "$function_name" -r "$region" -t "$timeout" -m "$memory_size" -a "$append_memory"

    # Checa o código de saída
    if [ $? -ne 0 ]; then
      echo ">>>> ERROR: Deploy failed for function $function_name with memory size $memory_size. Exiting..."
      exit 1
    fi
  done
fi

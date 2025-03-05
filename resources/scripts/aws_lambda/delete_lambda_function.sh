#!/bin/bash

# Initialize variables
function_name=""
region=""
skip_confirmation=false

# Parse command line arguments
while getopts "f:r:y" opt; do
  case $opt in
    f) function_name=$OPTARG ;;
    r) region=$OPTARG ;;
    y) skip_confirmation=true ;;
    *) echo "Usage: $0 -f <lambda_function_name> -r <region> [-y]"
       exit 1 ;;
  esac
done

# Check if function name and region were provided
if [ -z "$function_name" ] || [ -z "$region" ]; then
  echo "Usage: $0 -f <lambda_function_name> -r <region> [-y]"
  exit 1
fi

# Ask for user confirmation if not skipped
if [ "$skip_confirmation" = false ]; then
  read -p "Are you sure you want to delete the Lambda function '$function_name' in region '$region'? (y/n) [n]: " confirmation
  confirmation=${confirmation:-n}

  if [ "$confirmation" != "y" ]; then
    echo "Operation cancelled."
    exit 0
  fi
fi

# Delete the Lambda function
aws lambda delete-function --function-name "$function_name" --region "$region"

if [ $? -eq 0 ]; then
  echo -e "\n>>>> Lambda function '$function_name' deleted in region '$region'."
else
  echo -e "\n>>>> Failed to delete Lambda function '$function_name' in region '$region'."
fi
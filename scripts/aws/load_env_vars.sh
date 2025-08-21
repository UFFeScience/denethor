#!/bin/bash

export local_path="/home/marcello/Documents/denethor/"

# Load environment variables from .env file
echo "Loading environment variables..." ${local_path}.env
source ${local_path}.env

# Check for required environment variables
required_vars=(
    aws_region
    lambda_memory_sizes
    lambda_function_names
    lambda_s3_access_role
    denethor_db_host
    denethor_db_port
    denethor_db_database
    denethor_db_user
    denethor_db_password
    aws_account_id
    aws_access_key_id
    aws_secret_access_key
    key_name
    key_path
    ec2_instance_id
    ec2_instance_name
    ec2_instance_type
    ec2_path
    ec2_user
    vpc_id
    sg_id
    sg_name
    sg_description
    ami_id
    ami_name
)

# Check if any required environment variable is empty or undefined
missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "WARNING: The following environment variables are not defined or are empty:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    echo "------------------------------------"
else
    echo "All required environment variables are defined."
    echo "------------------------------------"
fi

# print the environment variables
echo "------------------------------------"
echo "Environment variables loaded:"
echo "------------------------------------"
for var in $(compgen -A variable | grep -E '^(aws_|ec2_|sg_|vpc_|ami_|key_)'); do
    echo "$var=${!var}"
done
echo "------------------------------------"
echo ""

#!/bin/bash

export local_path="/home/marcello/Documents/denethor/"

# Load environment variables from .env file
echo "Loading environment variables..." ${local_path}.env
source ${local_path}.env

# print the environment variables
echo "Environment variables loaded:"
echo "----------------------------"
for var in $(compgen -A variable | grep -E '^(aws_|ec2_|sg_|vpc_|ami_|key_)'); do
    echo "$var=${!var}"
done
echo "----------------------------"
echo ""

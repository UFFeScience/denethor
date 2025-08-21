#!/bin/bash

# Load environment variables
source ../load_env_vars.sh

echo "Creating IAM role for Lambda with S3 access"
aws iam create-role --role-name $lambda_role --assume-role-policy-document file://$(dirname "$0")/lambda_trust_policy.json --region $aws_region

echo "Checking if the role was created successfully"
aws iam get-role --role-name $lambda_role --region $aws_region > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Role creation failed."
    exit 1
fi

echo "Attaching AmazonS3FullAccess policy to the role"
aws iam attach-role-policy --role-name $lambda_role --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess --region $aws_region

echo "Role and policy attachment completed."

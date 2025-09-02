#!/bin/bash

# Load environment variables
source ../../load_env_vars.sh

echo "Creating IAM role for Lambda with S3 access"
aws iam create-role --role-name $LAMBDA_S3_ACCESS_ROLE --assume-role-policy-document file://lambda_trust_policy.json --region $AWS_REGION

echo "Attaching AmazonS3FullAccess policy to the role"
aws iam attach-role-policy --role-name $LAMBDA_S3_ACCESS_ROLE --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess --region $AWS_REGION

echo "Attaching AWSLambdaBasicExecutionRole policy to the role"
aws iam attach-role-policy --role-name $LAMBDA_S3_ACCESS_ROLE --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole --region $AWS_REGION

echo "Attaching AWSLambdaExecute policy to the role"
aws iam attach-role-policy --role-name $LAMBDA_S3_ACCESS_ROLE --policy-arn arn:aws:iam::aws:policy/AWSLambdaExecute --region $AWS_REGION

echo "Waiting for the role to be fully available..."
aws iam wait role-exists --role-name $LAMBDA_S3_ACCESS_ROLE --region $AWS_REGION

echo "Role is now available."

echo "Role and policy attachment completed."

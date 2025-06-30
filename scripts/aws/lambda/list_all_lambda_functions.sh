#!/bin/bash

# AWS region
region="sa-east-1"

echo "Listing all Lambda functions in region '$region'"

# List all Lambda functions in the specified region, sort them by LastModified, and print additional metadata to the console with headers
aws lambda list-functions --region "$region" --query "Functions[*].[FunctionName,Runtime,MemorySize,LastModified]" --output table | (sort -k1)

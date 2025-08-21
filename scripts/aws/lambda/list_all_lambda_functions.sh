#!/bin/bash

# Load environment variables
source ../load_env_vars.sh

echo "Listing all Lambda layers in region '$aws_region'"

aws lambda list-layers --region "$aws_region" --query "Layers[*].[LayerName,LatestMatchingVersion.Version,LatestMatchingVersion.Description,LatestMatchingVersion.CreatedDate]" --output table | (sort -k1)

echo "Listing all Lambda functions in region '$aws_region'"

# List all Lambda functions in the specified region, sort them by LastModified, and print additional metadata to the console with headers
aws lambda list-functions --region "$aws_region" --query "Functions[*].[FunctionName,Runtime,MemorySize,LastModified]" --output table | (sort -k1)
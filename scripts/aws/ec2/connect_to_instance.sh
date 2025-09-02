#!/bin/bash

# Load environment variables
source ../load_env_vars.sh

# Get instance ID from argument or use the environment variable
instance_id=${1:-$EC2_INSTANCE_ID}

# Notify if no instance ID is provided
if [ -z "$1" ]; then
  echo "No instance ID provided. Using default from environment variable: $EC2_INSTANCE_ID"
fi

# Retrieve the public DNS of the instance
instance_dns=$(aws ec2 describe-instances --instance-ids "$instance_id" \
  --query "Reservations[0].Instances[0].PublicDnsName" --output text)

# Connect to the EC2 instance
ssh -i "$KEY_PATH" ec2-user@"$instance_dns"

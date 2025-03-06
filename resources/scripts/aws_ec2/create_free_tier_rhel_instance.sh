#!/bin/bash

# AWS region
region="sa-east-1"

# Instance details
ami_id="ami-0c55b159cbfafe1f0" # Example AMI ID for RHEL, replace with the correct one for your region
instance_type="t2.micro"
key_name="your-key-pair-name" # Replace with your key pair name
security_group_id="sg-0123456789abcdef0" # Replace with your security group ID

echo "Launching a free-tier EC2 instance with RHEL in region '$region'"

# Run the instance
aws ec2 run-instances --image-id "$ami_id" --instance-type "$instance_type" --key-name "$key_name" --security-group-ids "$security_group_id" --region "$region" --query "Instances[0].InstanceId" --output text

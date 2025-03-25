#!/bin/bash

# Load environment variables
source ./env_vars.sh

# Connect to the EC2 instance
ssh -i "$key_path" ec2-user@"$ec2_instance_dns"

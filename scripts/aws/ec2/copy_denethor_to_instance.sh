#!/bin/bash

# Load environment variables
source ../load_env_vars.sh

# Define mappings for parameters
declare -A param_map=(
    ["src"]="conf/ src/ requirements_aws.txt"
    ["data"]="resources/data/full_dataset/"
    ["libs"]="resources/libs/clustalw-2.1-linux/"
)

# Validate input parameter
if [[ -z "${param_map[$1]}" ]]; then
    echo "Invalid parameter. Use one of: src, data, libs"
    echo "Usage: $0 {src | data | libs} [instance-id]"

    exit 1
fi

# Get the entries to copy based on the parameter
selected_entries=(${param_map[$1]})

# Check if key pair file exists
if [ ! -f "$key_path" ]; then
    echo "Key pair file not found: $key_path"
    exit 1
fi


# Check if instance ID is provided, otherwise use the environment variable
instance_id=${2:-$ec2_instance_id}

# Retrieve the public DNS of the instance
instance_dns=$(aws ec2 describe-instances --instance-ids "$instance_id" --region "$aws_region" --query "Reservations[0].Instances[0].PublicDnsName" --output text)

if [ -z "$instance_dns" ]; then
    echo "Failed to retrieve the public DNS for instance ID: $instance_id"
    exit 1
fi

# Process each selected entry
for entry in "${selected_entries[@]}"; do
    # Delete existing files in the EC2 instance
    echo "Deleting $entry in the EC2 instance..."
    ssh -i "$key_path" $ec2_user@"$instance_dns" "rm -rf ${ec2_path}${entry}"

    # Ensure the remote directory exists
    echo "Creating directory $entry in the EC2 instance..."
    dir=$(dirname "${ec2_path}${entry}")
    ssh -i "$key_path" $ec2_user@"$instance_dns" "mkdir -p $dir"

    # Copy entry to the EC2 instance
    echo "Copying $entry to the EC2 instance..."
    if [[ -d "${local_path}${entry}" ]]; then
        scp -i "$key_path" -r "${local_path}${entry}" $ec2_user@"$instance_dns":"${ec2_path}${entry}"
    else
        scp -i "$key_path" "${local_path}${entry}" $ec2_user@"$instance_dns":"${ec2_path}${entry}"
    fi
done

# If requirements file was copied, install the dependencies
if [[ " ${selected_entries[@]} " =~ " requirements_aws.txt " ]]; then
    echo "Installing dependencies in the EC2 instance..."
    ssh -i "$key_path" $ec2_user@"$instance_dns" "python3.11 -m pip install -r ${ec2_path}requirements_aws.txt"
fi

echo "Ensuring the logs directory exists in the EC2 instance..."
ssh -i "$key_path" $ec2_user@"$instance_dns" "mkdir -p ${ec2_path}resources/logs/aws_ec2"
ssh -i "$key_path" $ec2_user@"$instance_dns" "test -d ${ec2_path}resources/logs/aws_ec2 && echo 'Logs directory exists.'"

echo "Ensuring the .tmp directory exists in the EC2 instance..."
ssh -i "$key_path" $ec2_user@"$instance_dns" "mkdir -p ${ec2_path}.tmp"
ssh -i "$key_path" $ec2_user@"$instance_dns" "test -d ${ec2_path}.tmp && echo '.tmp directory exists.'"
#!/bin/bash

# Load environment variables
source ./env_vars.sh

# List of files and directories to copy
entries=(
    "conf/"
    "resources/data/full_dataset/"
    "resources/libs/clustalw-2.1-linux/"
    "src/"
    "requirements_aws.txt"
)

# Check if key pair file exists
if [ ! -f "$key_path" ]; then
    echo "Key pair file not found: $key_path"
    exit 1
fi

# Display menu to select entries
echo ""
echo "Select the entry to load:"
echo "--------------------------"
for i in "${!entries[@]}"; do
    echo "$i) ${entries[$i]}"
done
echo "--------------------------"
echo "a) All"
echo "q) Quit"
echo ""
read -p "Enter your choice: " choice

if [ "$choice" == "q" ]; then
    echo "Aborting..."
    exit 0
elif [ "$choice" == "a" ]; then
    selected_entries=("${entries[@]}")
else
    selected_entries=("${entries[$choice]}")
fi

# Process each selected entry
for entry in "${selected_entries[@]}"; do

    # Delete existing files in the EC2 instance
    echo "Deleting $entry in the EC2 instance..."
    ssh -i "$key_path" $ec2_user@"$ec2_instance_dns" "rm -rf ${ec2_path}${entry}"

    # Ensure the remote directory exists
    echo "Creating directory $entry in the EC2 instance..."
    dir=$(dirname "${entry}")
    ssh -i "$key_path" $ec2_user@"$ec2_instance_dns" "mkdir -p $dir"

    # Copy entry to the EC2 instance
    echo "Copying $entry to the EC2 instance..."
    if [[ -d "${local_path}${entry}" ]]; then
        scp -i "$key_path" -r "${local_path}${entry}" $ec2_user@"$ec2_instance_dns":"${ec2_path}${entry}"
    else
        scp -i "$key_path" "${local_path}${entry}" $ec2_user@"$ec2_instance_dns":"${ec2_path}${entry}"
    fi
done
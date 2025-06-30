#!/bin/bash

# Load environment variables
source ../load_env_vars.sh

# Check if key pair file exists
if [ ! -f "$key_path" ]; then
    echo "Key pair file not found: $key_path"
    exit 1
fi

# Verificar se o termo de busca foi fornecido como argumento
if [ -z "$1" ]; then
    echo "Usage: $0 <search_term> [instance_id]"
    exit 1
fi

search_term=$1

# Check if instance ID is provided, otherwise use the environment variable
instance_id=${2:-$ec2_instance_id}

if [ -z "$2" ]; then
    echo "No instance ID provided. Using default instance ID from environment variable: $ec2_instance_id"
fi

# Retrieve the public DNS of the instance
instance_dns=$(aws ec2 describe-instances --instance-ids "$instance_id" --region "$aws_region" --query "Reservations[0].Instances[0].PublicDnsName" --output text)

if [ -z "$instance_dns" ]; then
    echo "Failed to retrieve the public DNS for instance ID: $instance_id"
    exit 1
fi

# Listar os arquivos de log que correspondem ao termo de busca no diretório remoto
matching_files=$(ssh -i "$key_path" $ec2_user@"$instance_dns" "ls ${ec2_path}resources/logs/aws_ec2 | grep '$search_term'")

if [ -z "$matching_files" ]; then
    echo "No files found containing '$search_term' in ${ec2_path}resources/logs/aws_ec2."
    exit 1
fi

# Copiar os arquivos de log correspondentes para a máquina local
echo "Copying files containing '$search_term' from the EC2 instance to ${local_path}resources/logs/aws_ec2/"
for file in $matching_files; do
    scp -i "$key_path" $ec2_user@"$instance_dns":"${ec2_path}resources/logs/aws_ec2/$file" "${local_path}resources/logs/aws_ec2/"
done
echo "Files copied successfully."

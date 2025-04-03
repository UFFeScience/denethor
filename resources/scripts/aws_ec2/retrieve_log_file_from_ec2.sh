#!/bin/bash

# Load environment variables
source ./env_vars.sh

# Check if key pair file exists
if [ ! -f "$key_path" ]; then
    echo "Key pair file not found: $key_path"
    exit 1
fi

# Verificar se o termo de busca foi fornecido como argumento
if [ -z "$1" ]; then
    echo "Usage: $0 <search_term>"
    exit 1
fi

search_term=$1

# Listar os arquivos que correspondem ao termo de busca no diretório remoto
echo "Listing log files containing '$search_term' in the EC2 instance..."
matching_logs=$(ssh -i "$key_path" $ec2_user@"$ec2_instance_dns" "ls ${ec2_path}resources/logs/aws_ec2 | grep '$search_term'")

if [ -z "$matching_logs" ]; then
    echo "No log files found containing '$search_term' in ${ec2_path}resources/logs/aws_ec2."
    exit 1
fi

echo "$matching_logs"

# Copiar os arquivos de log correspondentes para a máquina local
echo "Copying log files containing '$search_term' from the EC2 instance to ${local_path}resources/logs/aws_ec2/"
for log_file in $matching_logs; do
    scp -i "$key_path" $ec2_user@"$ec2_instance_dns":"${ec2_path}resources/logs/aws_ec2/$log_file" "${local_path}resources/logs/aws_ec2/"
done
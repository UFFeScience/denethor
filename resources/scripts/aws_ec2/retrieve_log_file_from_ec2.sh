#!/bin/bash

# Load environment variables
source ./env_vars.sh

# Check if key pair file exists
if [ ! -f "$key_path" ]; then
    echo "Key pair file not found: $key_path"
    exit 1
fi

# Verificar se o prefixo foi fornecido como argumento
if [ -z "$1" ]; then
    echo "Usage: $0 <file_prefix>"
    exit 1
fi

file_prefix=$1

# Listar os arquivos que correspondem ao prefixo no diretório remoto
echo "Listing log files with prefix '$file_prefix' in the EC2 instance..."
matching_logs=$(ssh -i "$key_path" $ec2_user@"$ec2_instance_dns" "ls ${ec2_path}resources/logs/aws_ec2 | grep '^$file_prefix'")

if [ -z "$matching_logs" ]; then
    echo "No log files found with prefix '$file_prefix' in ${ec2_path}resources/logs/aws_ec2."
    exit 1
fi

echo "$matching_logs"

# Copiar os arquivos de log correspondentes para a máquina local
echo "Copying log files with prefix '$file_prefix' from the EC2 instance to ${local_path}resources/logs/aws_ec2/"
for log_file in $matching_logs; do
    scp -i "$key_path" $ec2_user@"$ec2_instance_dns":"${ec2_path}resources/logs/aws_ec2/$log_file" "${local_path}resources/logs/aws_ec2/"
done
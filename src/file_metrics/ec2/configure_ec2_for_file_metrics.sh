#!/bin/bash

# Carrega variáveis de ambiente
source ../../../scripts/aws/load_env_vars.sh

# Recupera DNS público da instância
instance_dns=$(aws ec2 describe-instances --instance-ids "$EC2_INSTANCE_ID" \
  --query "Reservations[0].Instances[0].PublicDnsName" --output text)

if [ -z "$instance_dns" ]; then
  echo "Não foi possível obter o DNS da instância."
  exit 1
fi

echo "Conectando na instância: $instance_dns"


# Verifica e instala pip e dependências, e configura o AWS CLI
ssh -i "$KEY_PATH" "$EC2_USER@$instance_dns" "
set -e
echo \"Configurando AWS CLI...\"
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set region $AWS_REGION
echo \"AWS CLI configurado.\"

echo \"Atualizando pacotes...\"
if [ -f /etc/os-release ] && grep -qi \"amazon linux\" /etc/os-release; then
  sudo yum update -y
  sudo yum install python3-pip -y
else
  sudo apt update
  sudo apt install python3-pip -y
fi

echo \"Instalando boto3...\"
python3 -m pip install --user boto3
"

echo "Configuração da instância EC2 concluída."

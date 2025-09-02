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

# Cria diretório file_metrics na home do usuário remoto
ssh -i "$KEY_PATH" "$EC2_USER@$instance_dns" "mkdir -p ~/file_metrics"

# Copia o arquivo file_metrics_ec2.py para a instância
scp -i "$KEY_PATH" file_metrics_ec2.py "$EC2_USER@$instance_dns:~/file_metrics/file_metrics.py"

# Verifica e instala pip e dependências
ssh -i "$KEY_PATH" "$EC2_USER@$instance_dns" << 'EOF'
set -e
echo "Atualizando pacotes..."
if [ -f /etc/os-release ] && grep -qi "amazon linux" /etc/os-release; then
  sudo yum update -y
  sudo yum install python3-pip -y
else
  sudo apt update
  sudo apt install python3-pip -y
fi

echo "Instalando boto3..."
python3 -m pip install --user boto3
EOF

echo "Arquivo file_metrics.py
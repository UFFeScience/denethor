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

# Cria diretório file_metrics na home do usuário remoto, se não existir
ssh -i "$KEY_PATH" "$EC2_USER@$instance_dns" "mkdir -p ~/file_metrics"

# Copia o arquivo file_metrics_ec2.py para a instância
scp -i "$KEY_PATH" file_metrics_ec2.py "$EC2_USER@$instance_dns:~/file_metrics/file_metrics.py"

echo "Arquivo file_metrics.py copiado para a instância EC2."

REMOTE_OUTPUT_DIR="~/file_metrics/"
LOCAL_OUTPUT_DIR="logs"

# S3_PREFIX=data/test_download_files/
# S3_PREFIX=subtree/
S3_PREFIX=$DENETHOR_S3_FULL_DATASET

# Cria o diretório de saída remoto e executa o script
echo "Executando o script file_metrics.py na instância EC2..."
ssh -t -i "$KEY_PATH" "$EC2_USER@$instance_dns" "mkdir -p $REMOTE_OUTPUT_DIR && python3 -u ~/file_metrics/file_metrics.py $DENETHOR_S3_BUCKET $S3_PREFIX $REMOTE_OUTPUT_DIR"

if [ $? -ne 0 ]; then
  echo "A execução do script na instância EC2 falhou."
  exit 1
fi

echo "Execução concluída. Copiando o relatório para a máquina local..."

# Encontra o relatório mais recente na instância remota
latest_report=$(ssh -i "$KEY_PATH" "$EC2_USER@$instance_dns" "ls -t $REMOTE_OUTPUT_DIR/download_report_*.json | head -n 1")

if [ -z "$latest_report" ]; then
  echo "Nenhum arquivo de relatório encontrado na instância."
  exit 1
fi

# Cria o diretório de saída local, se não existir
mkdir -p "$LOCAL_OUTPUT_DIR"

# Copia o arquivo de relatório para o diretório local
scp -i "$KEY_PATH" "$EC2_USER@$instance_dns:$latest_report" "$LOCAL_OUTPUT_DIR"

if [ $? -eq 0 ]; then
  echo "Relatório copiado com sucesso para $LOCAL_OUTPUT_DIR"
else
  echo "Falha ao copiar o relatório."
  exit 1
fi

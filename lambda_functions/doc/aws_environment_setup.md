# Preparação do ambiente na AWS

Para a execução dos comandos abaixo, assumimos que o usuário já possui uma conta na AWS e está de posse do `AWS Access Key ID` e `AWS Secret Access Key`. Caso contrário, será necessário criar uma conta na AWS e obter as credenciais de acesso.

## Configurar o acesso via AWS CLI na máquina local

Para configurar o acesso via AWS CLI na máquina local, é necessário baixar o zip da aplicação e descompactá-lo:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

aws --version
# aws-cli/2.13.37 Python/3.11.6 Linux/6.2.0-36-generic exe/x86_64.ubuntu.22 prompt/off
```

```bash
aws configure
```

Saída esperada:

```bash
AWS Access Key ID: ...............
AWS Secret Access Key: ...........................
Default region name: sa-east-1
Default output format: json
```

## Criar Bucket S3

Será necessário criar três buckets S3 para execução do workflow na AWS Lambda:

1. Um bucket para armazenar os arquivos de entrada;
2. Um bucket para armazenar os arquivos de saída da etapa de construção de árvores filogenéticas;
3. Um bucket para armazenar os arquivos de saída da etapa de mineração de subárvores.

Para isso, execute os seguintes comando no terminal:

```bash
aws s3api create-bucket --bucket mribeiro-input-files --region sa-east-1 --create-bucket-configuration LocationConstraint=sa-east-1

aws s3api create-bucket --bucket mribeiro-tree-files --region sa-east-1 --create-bucket-configuration LocationConstraint=sa-east-1

aws s3api create-bucket --bucket mribeiro-subtree-files --region sa-east-1 --create-bucket-configuration LocationConstraint=sa-east-1
```

Para verificar se os buckets foram criados corretamente:

```bash
aws s3api list-buckets
```

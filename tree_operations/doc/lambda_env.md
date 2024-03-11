# Preparação do ambiente para criação das Funções Lambda

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

## Criar uma camada base para a função lambda

Antes de criar as funções lambda, é necessário criar uma camada base para a função. Para isso, é preciso criar um diretório chamado `package` e, em seguida, instalar as dependências do projeto e copiar o executável do ClustalW. Por fim, compactar o diretório em um arquivo .zip para ser utilizado na criação da camada.

```bash
mkdir package

python3.11 -m pip install --target package/python -r requirements.txt

cp -R clustalw-2.1-linux-x86_64-libcppstatic package/python

cd package

zip -r ../lambda_layer.zip .
```

A criação da camada base na AWS deve indicar o interpretador que será utilizado (Python 3.11) e o *arquivo zip* (criado anteriormente) que contém as dependências do projeto.

```bash
aws lambda publish-layer-version --layer-name lambda_layer \
--zip-file ./lambda_layer.zip \
--compatible-runtimes python3.11 \
--region sa-east-1
```

## Criar funções lambda

Para executar o workflow na AWS Lambda, é necessário criar duas Funções Lambda: uma para a construção de árvores filogenéticas e outra para a análise de subárvores.

### Função Tree Constructor

Essa será a Função Lambda para a atividade de construção de Árvores Filogenéticas. inicialmente, é necessário criar um arquivo .zip contendo o código da função lambda e as dependências do projeto.

```bash
cd tree_operations 
zip tree_constructor.zip tree_constructor_core.py tree_constructor_lambda.py file_operations.py
```

Em seguida podemos criar a função lambda na AWS. Substitua `[xxxxxxxxxxxxx]` pelo número da sua conta na AWS:

```bash
aws lambda create-function --function-name tree_constructor \
--zip-file tree_constructor.zip \
--handler tree_constructor_lambda.handler \
--runtime python3.11 \
--role arn:aws:iam::[xxxxxxxxxxxxx]:role/Lambda_S3_access_role \
--timeout 15 \
--memory-size 128 \
--region sa-east-1 \
--layers arn:aws:lambda:sa-east-1:[xxxxxxxxxxxxx]:layer:lambda_layer:1
```

### Função Subtree Mining

Essa será a Função Lambda para a atividade de mineração de subárvores. inicialmente, é necessário criar um arquivo .zip contendo o código da função lambda e as dependências do projeto.

```bash
cd tree_operations
zip subtree_mining.zip subtree_mining_core.py subtree_mining_lambda.py file_operations.py
```

Em seguida podemos criar a função lambda na AWS. Substitua `[xxxxxxxxxxxxx]` pelo número da sua conta na AWS:

```bash
aws lambda create-function --function-name subtree_mining \
--zip-file subtree_mining.zip \
--handler subtree_mining_lambda.handler \
--runtime python3.11 \
--role arn:aws:iam::[xxxxxxxxxxxxx]:role/Lambda_S3_access_role \
--timeout 900 \
--memory-size 256 \
--region sa-east-1 \
--layers arn:aws:lambda:sa-east-1:[xxxxxxxxxxxxx]:layer:lambda_layer:1
```

Note que o tempo limite para a execução da função `subtree_mining` foi definido como 900 segundos (15 minutos) e o tamanho da memória foi definido como 256 MB. Esses valores são necessários pois essa atividade executa por um período de tempo maior que a anterior, visto que realiza comparações entre as subárvores.














- Python 3.11
- Clustalw (versão 2.1)
- Arquivo FASTA com sequências de proteínas

## Clustal

Linux: <http://www.clustal.org/download/current/clustalw-2.1-linux-x86_64-libcppstatic.tar.gz>
Windows: <http://www.clustal.org/download/current/clustalw-2.1-win.msi>

## Instalação de Dependências

Antes de executar o projeto, é necessário instalar as dependências do Python especificadas no arquivo "requirements.txt". Para isso, execute o seguinte comando no terminal:

```bash
pip install -r requirements.txt
```

## Organização dos Arquivos

Certifique-se de que todos os arquivos necessários, incluindo as sequências de proteínas no formato FASTA, estejam no diretório especificado em 'INPUT_PATH'.

## Etapas do Workflow

### 1. Construção de Árvores Filogenéticas

O primeiro passo do workflow é a construção de árvores filogenéticas a partir das sequências de proteínas fornecidas. Para isso, execute o script "tree_constructor_local.py":

```bash
python tree_constructor_local.py
```

Esse script realiza o alinhamento múltiplo das sequências usando o ClustalW e, em seguida, constrói a árvore filogenética utilizando o método Neighbor-Joining (NJ).

### 2. Construção de Subárvores e Análise de MAF

Após a construção das árvores filogenéticas, o próximo passo é gerar subárvores a partir das árvores principais e realizar a análise de MAF (matriz de frequência de pares de subárvores).

Execute o script "subtree_mining_local.py":

```bash
python subtree_mining_local.py
```

Esse script irá gerar todas as subárvores a partir das árvores filogenéticas e, em seguida, calcular a matriz de frequência de pares de subárvores (MAF). O resultado será exibido no terminal.

### Saída

As subárvores geradas serão salvas no diretório "PATH_OUTPUT". Além disso, a matriz de frequência de pares de subárvores (MAF) será exibida no terminal durante a execução do script.

### Limpeza de Arquivos Temporários

Os scripts realizarão automaticamente a limpeza dos arquivos temporários gerados durante o processo, bem como de execuções antigas. Os arquivos temporários serão excluídos do diretório "TMP_PATH".

## Considerações Finais

Este guia fornece uma visão geral do workflow para construção de árvores filogenéticas e análise de subárvores. Certifique-se de que os arquivos de entrada estejam corretamente organizados nos diretórios indicados e execute os scripts conforme as etapas descritas.

## Licença

Este projeto está licenciado sob a [MIT License](https://opensource.org/licenses/MIT).


# Execução através do AWS Lambda

## Pré-requisitos

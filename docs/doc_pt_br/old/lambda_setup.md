# Preparação das Funções Lambda

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
--zip-file fileb://lambda_layer.zip \
--compatible-runtimes python3.11 \
--region sa-east-1
```

## Função Tree Constructor

Essa será a Função Lambda para a atividade de construção de Árvores Filogenéticas. inicialmente, é necessário criar um arquivo .zip contendo o código da função lambda e as dependências do projeto.

```bash
cd lambda_functions/src 
zip tree_constructor.zip tree_constructor_core.py tree_constructor_lambda.py file_utils.py
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

## Função Subtree Mining

Essa será a Função Lambda para a atividade de mineração de subárvores. inicialmente, é necessário criar um arquivo .zip contendo o código da função lambda e as dependências do projeto.

```bash
cd lambda_functions/src
zip subtree_mining.zip subtree_mining_core.py subtree_mining_lambda.py file_utils.py
```

Em seguida podemos criar a função lambda na AWS. Substitua `[xxxxxxxxxxxxx]` pelo número da sua conta na AWS:

```bash
aws lambda create-function --function-name subtree_mining \
--zip-file fileb://subtree_mining.zip \
--handler subtree_mining_lambda.handler \
--runtime python3.11 \
--role arn:aws:iam::[xxxxxxxxxxxxx]:role/Lambda_S3_access_role \
--timeout 900 \
--memory-size 256 \
--region sa-east-1 \
--layers arn:aws:lambda:sa-east-1:[xxxxxxxxxxxxx]:layer:lambda_layer:1
```

Note que o tempo limite para a execução da função `subtree_mining` foi definido como 900 segundos (15 minutos) e o tamanho da memória foi definido como 256 MB. Esses valores são necessários pois essa atividade executa por um período de tempo maior que a anterior, visto que realiza comparações entre as subárvores.

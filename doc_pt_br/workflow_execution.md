# Sistema `Denethor`

Denethor é composto por um conjunto de ferramentas e scripts que permitem a execução de workflows em ambientes de computação em nuvem. Permite controlar a execução de workflows e coletar estatísticas de execução e proveniência.

## `workflow_executor.py`

O `workflow_executor.py` é um script composto por uma série de passos e funções que orquestra a execução do projeto. Ele se baseia tanto em parâmetros determinados nos arquivos de configuração `json`, quanto em parâmetros obtidos em tempo de execução, para realizar a execução de cada etapa.

### `workflow_steps.json`

O arquivo `workflow_steps.json` contém as etapas do workflow que serão executadas, representadas pela lista `steps`. Cada objeto dentro de `steps` contém:

- `name`: O nome da etapa.
- `module`: O módulo Python que contém a função a ser executada nesta etapa.
- `handler`: O nome da função a ser executada nesta etapa.
- `active`: Um booleano que indica se a etapa está ativa ou não. Se `active` for `False`, a etapa será ignorada durante a execução do workflow.
- `params`: Um objeto que contém parâmetros específicos e necessários para a execução da etapa.

Os parâmetros variam dependendo da etapa, mas podem incluir:

- `bucket`: O nome do bucket AWS S3 para upload/download de arquivos.
- `key`: A chave do arquivo a ser acessado no bucket AWS S3.
- `function_name`: O nome da função AWS Lambda a ser invocada.
- `inputBucket`: O nome do bucket AWS S3 de onde os arquivos de entrada serão lidos.
- `inputKey`: A chave do arquivo de entrada a ser lido do bucket AWS S3, se aplicável.
- `outputBucket`: O nome do bucket AWS S3 onde os arquivos de saída serão escritos.
- `outputKey`: A chave do arquivo de saída a ser escrito no bucket AWS S3, se aplicável.
- `execution_strategy`: A estratégia de execução para a função AWS Lambda. Pode ser *for_each_file* ou *for_all_files*.

### `workflow_conf.json`

O arquivo `workflow_conf.json` contém informações sobre o workflow, as atividades que o compõem e as estatísticas que devem ser coletadas. O arquivo é composto por um objeto principal `workflow` que contém:

- `workflow_name`: Nome do workflow.

- `workflow_description`: Descrição do workflow.

- `input_files`: Objeto que contém informações sobre os arquivos de entrada para o workflow.

  - `json_file`: Caminho para o arquivo JSON de entrada.

  - `limit`: Número máximo de arquivos de entrada a serem processados.

- `activities`: Lista de atividades que compõem o workflow. Cada atividade é um objeto que contém:

  - `activity_name`: Nome da atividade.
  
  - `activity_description`: Descrição da atividade.
  
  - `provider_name`: Nome do provedor de serviços onde a atividade será executada.
  
  - `custom_statistics`: Objeto que contém as estatísticas personalizadas a serem coletadas para a atividade. Cada estatística contém:

    - `searchKey`: Chave a ser buscada nos logs para coletar a estatística.

    - `fieldName`: Nome do campo no banco de dados onde a estatística será armazenada.

    - `dataType`: Tipo de dados da estatística.

    - `description`: *(opcional)* Descrição da estatística.

    - `separator`: *(opcional)* Separador a ser usado ao analisar os logs daquela chave de busca.

- `default_separator`: O separador padrão a ser usado ao analisar os logs, caso um específico não seja fornecido na definição da estatística.

- `general_statistics`: Um objeto que contém as estatísticas gerais a serem coletadas para o workflow. Os atributos são semelhantes aos das estatísticas personalizadas descritas acima, mas são coletadas para todo o workflow, não apenas para atividades individuais.

### `provider_conf.json`

O arquivo `provider_conf.json` contém informações sobre os provedores de serviços que são usados para executar atividades em um workflow. Essas informações são usadas para determinar os recursos que serão alocados para cada atividade executada. Cada provedor é representado por um objeto dentro do array `providers`:

- `provider_name`:Nome do provedor de serviços. No exemplo fornecido, os provedores são versões diferentes do AWS Lambda, diferenciadas pelo tempo máximo de execução permitido (em segundos).

- `provider_ram`: Quantidade de RAM alocada no provedor de serviços, em megabytes.

- `provider_timeout`: Tempo máximo de execução permitido para a atividade (função lambda) no provedor de serviços, em segundos.

- `provider_cpu`: O número de unidades de CPU alocadas no provedor de serviços.

- `provider_storage_mb`: A quantidade de armazenamento alocado no provedor de serviços, em megabytes.

## Etapas para execução do workflow e extração de estatísticas

Conforme definido no arquivo `workflow_steps.json`, o workflow é composto por 7 etapas:

1. **Upload files to AWS S3**: Esta etapa realiza o upload de arquivos para o bucket AWS S3 especificado. O parâmetro "key" não é especificado, indicando que os arquivos serão carregados diretamente na raiz do bucket.

2. **Invoke function execution (tree_constructor)**: Esta etapa realiza a invocação da função AWS Lambda "tree_constructor". A função lê arquivos do bucket de entrada e escreve a saída no bucket de saída. A estratégia de execução é "for_each_file", fazendo com que a função seja invocada separadamente para cada arquivo de entrada.

3. **Monitor function execution (tree_constructor)**: Esta etapa realiza o monitoramento da execução da função AWS Lambda "tree_constructor". Através dos requests_id gerados na etapa anterior, é possível monitorar o status da execução de cada chamada da função.

4. **Invoke function execution (subtree_mining)**: Esta etapa realiza a invocação da função AWS Lambda "subtree_mining". A função lê arquivos do bucket de entrada e escreve a saída no bucket de saída. A estratégia de execução é "for_all_files", fazendo com que a função seja invocada uma úncia vez para todo o conjunto de arquivos de entrada.

5. **Monitor function execution (subtree_mining)**: Esta etapa realiza o monitoramento da execução da função AWS Lambda "subtree_mining". Através dos requests_id gerados na etapa anterior, é possível monitorar o status da execução da função.

6. **Download produced files from AWS S3**: Esta etapa realiza o download de arquivos produzidos a partir do bucket AWS S3 especificado. Os arquivos são baixados para o caminho indicado em "downloadPath".

7. **Import Provenance from AWS CloudWatch Logs**: Esta etapa realiza a importação de dados de proveniência e demais estatísticas de execução a partir dos logs das funções armazenados no AWS CloudWatch. Os logs serão salvos em arquivos separados para cada função ("tree_constructor" e "subtree_mining") no caminho indicado em "logPath". Além disso, as estatísticas coletadas são salvas em um banco de dados relacional, permitindo a análise e visualização dos dados.

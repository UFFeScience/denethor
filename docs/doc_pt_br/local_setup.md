# Preparação do ambiente execução local do Workflow

Para a execução do workflow na máquina local, é necessário ter o `Python 3.11` e o gerenciador de pacotes `Pip` instalados. Além disso, é necessário ter software o [ClustalW](http://www.clustal.org/clustal2/) instalado. Todas essas etapas foram descritas no arquivo [README.md](../README.md).

A partir desse ponto, as intruções assumem que o projeto já foi clonado do repositório git e que o ambiente já está configurado.

## Instalação de Dependências

Antes de executar o projeto, é necessário instalar as dependências do Python especificadas no arquivo "requirements.txt". Para isso, execute o seguinte comando no terminal:

```bash
pip install -r requirements.txt
```

## Organização dos Arquivos

Certifique-se de que todos os arquivos necessários (contendo as sequências de proteínas no formato FASTA) estejam no diretório especificado em `INPUT_PATH`.

## Etapas do Workflow

### 1. Construção de Árvores Filogenéticas

O primeiro passo do workflow é a construção de árvores filogenéticas a partir das sequências de proteínas fornecidas. Para isso, execute o script `tree_constructor_local.py`:

```bash
python tree_constructor_local.py
```

Esse script realiza o alinhamento múltiplo das sequências usando o ClustalW e, em seguida, constrói a árvore filogenética utilizando o método Neighbor-Joining (NJ).

### 2. Construção de Subárvores e Análise de MAF

Após a construção das árvores filogenéticas, o próximo passo é gerar subárvores a partir das árvores principais e realizar a análise de MAF (matriz de frequência de pares de subárvores).

Execute o script `subtree_mining_local.py`:

```bash
python subtree_mining_local.py
```

Esse script irá gerar todas as subárvores a partir das árvores filogenéticas e, em seguida, calcular a matriz de frequência de pares de subárvores (MAF). O resultado será exibido no terminal.

### Saída

As subárvores geradas serão salvas no diretório `PATH_OUTPUT`. Além disso, a matriz de frequência de pares de subárvores (MAF) será exibida no terminal durante a execução do script.

### Limpeza de Arquivos Temporários

Os scripts realizarão automaticamente a limpeza dos arquivos temporários gerados durante o processo, bem como de execuções antigas. Os arquivos temporários serão excluídos do diretório `TMP_PATH`.

## Considerações Finais

Este guia fornece uma visão geral do workflow para construção de árvores filogenéticas e análise de subárvores. Certifique-se de que os arquivos de entrada estejam corretamente organizados nos diretórios indicados e execute os scripts conforme as etapas descritas.

## Licença

Este projeto está licenciado sob a [MIT License](https://opensource.org/licenses/MIT).

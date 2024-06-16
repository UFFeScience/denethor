# Pré-requisitos gerais do ambiente de desenvolvimento

Os comandos aqui descritos foram criados com base no sistema operacional Ubuntu 22.04 e podem ter que ser adaptados para outros sistemas operacionais.

## Instalação do Python 3.11 e Pip

Para preparar os pacotes de função Lambda, é necessário ter o `Python 3.11` e o gerenciador de pacotes `Pip` instalados na máquina local. Para verificar se o Python 3.11 está instalado, execute o seguinte comando no terminal:

```bash
python3.11 --version
```

Se o Python 3.11 não estiver instalado, é possível realizar a instalação através do seguinte comando:

```bash
sudo apt-get install python3.11
python3.11 --version
# Python 3.11.0rc1

ls /usr/bin/python*
```

Para verificar se o Pip está instalado, execute o seguinte comando no terminal:

```bash
pip --version
```

Se o Pip não estiver instalado, é possível realizar a instalação através do seguinte comando:

```bash
sudo apt-get install pip
pip --version
# pip 22.0.2 from /usr/lib/python3/dist-packages/pip (python 3.10)
```

## Instalação do ClustalW

Para a execução do workflow, é necessário ter o [ClustalW](http://www.clustal.org/clustal2/) instalado. O ClustalW é um software de alinhamento múltiplo de sequências de proteínas. Uma das formas de obter este software é descrita a seguir:

```bash
sudo apt-get install curl

curl "http://www.clustal.org/download/current/clustalw-2.1-linux-x86_64-libcppstatic.tar.gz" -O

tar -xvzf clustalw-2.1-linux-x86_64-libcppstatic.tar.gz
```

Caso esteja utilizando o sistema operacional Windows, é possível baixar o instalador do ClustalW neste link: [Download ClustalW para Windows](http://www.clustal.org/download/current/clustalw-2.1-win.msi)

## Tipos de execução

É possível executar o projeto em dois modos: *local* e *lambda*.

- O modo *local* irá executar todo o workflow na máquina local
- O modo *lambda* deve ser usado para execução utilizando as funções AWS Lambda.

Cada modo de execução possui suas próprias instruções e configurações específicas. Elas estão detalhadas nos arquivos [local_env](docs/local_env.md) e [lambda_env](lambda_functions\doc\aws_environment_setup.md), respectivamente.

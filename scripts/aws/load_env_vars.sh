#!/bin/bash


env_file="/home/marcello/Documents/denethor/.env"

# Lista das variáveis obrigatórias
required_vars=(
    DENETHOR_PATH
    PYTHON_VERSION
    PYTHON_RUNTIME
    SLEEP_DURATION
    AWS_REGION
    LAMBDA_FUNCTION_NAMES
    LAMBDA_DEFAULT_TIMEOUTS
    LAMBDA_DEFAULT_MEMORY
    LAMBDA_MEMORY_SIZES
    BASE_LAYER_NAME
    DENETHOR_LAYER_NAME
    LAMBDA_S3_ACCESS_ROLE
    DENETHOR_DB_HOST
    DENETHOR_DB_PORT
    DENETHOR_DB_DATABASE
    DENETHOR_DB_USER
    DENETHOR_DB_PASSWORD
    AWS_ACCOUNT_ID
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    KEY_NAME
    KEY_PATH
    EC2_INSTANCE_ID
    EC2_INSTANCE_NAME
    EC2_INSTANCE_TYPE
    EC2_PATH
    EC2_USER
    VPC_ID
    SG_ID
    SG_NAME
    SG_DESCRIPTION
    AMI_ID
    AMI_NAME
)


# Função para imprimir variáveis de ambiente de um array passado por parâmetro
print_vars() {
    local arr=("${@}")
    echo "------------------------------------"
    echo "Variables:"
    echo "------------------------------------"
    for var in "${arr[@]}"; do
        echo "$var=${!var}"
    done
    echo "------------------------------------"
    echo ""
}

echo "Loading environment variables... ${env_file}"
source ${env_file}

# Final check if any required environment variable is empty or undefined
missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "Some required environment variables are missing:"
    print_vars "${missing_vars[@]}"
    exit 1
else
    echo -e "All required environment variables are defined.\n"
fi



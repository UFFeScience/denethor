import boto3
import os

import boto3
import os

def download_files_from_path(bucket_name, bucket_path, destination_folder):
    # Cria um cliente S3
    s3 = boto3.client('s3')

    # Lista os objetos no bucket com o prefixo especificado
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=bucket_path)

    # Verifica se há arquivos no caminho especificado
    if 'Contents' not in response:
        print(f"O caminho '{bucket_path}' no bucket '{bucket_name}' está vazio ou não existe.")
        return

    # Baixa cada arquivo
    for obj in response['Contents']:
        file_name = obj['Key']
        # Remove o prefixo do caminho para salvar localmente
        relative_path = os.path.relpath(file_name, bucket_path)
        destination_path = os.path.join(destination_folder, relative_path)

        # Cria diretórios, se necessário
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        print(f"Baixando {file_name} para {destination_path}...")
        s3.download_file(bucket_name, file_name, destination_path)

    print("Download concluído.")


# Exemplo de uso
bucket_name = 'denethor'
bucket_path = 'tree'  # Exemplo: 'pasta/subpasta/'
destination_folder = 'resources/data/tree_files'
download_files_from_path(bucket_name, bucket_path, destination_folder)

bucket_path = 'subtree'  # Exemplo: 'pasta/subpasta/'
destination_folder = 'resources/data/subtree_files'
download_files_from_path(bucket_name, bucket_path, destination_folder)

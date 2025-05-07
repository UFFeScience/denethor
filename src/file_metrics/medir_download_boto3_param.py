import boto3
import time
import os
import sys

def medir_taxa_download_boto3_param(bucket_name, prefix, diretorio_local):
    """
    Baixa arquivos de um bucket S3 usando boto3 e mede a taxa de download.
    Recebe bucket_name, prefix e diretorio_local como parâmetros.

    Args:
        bucket_name (str): O nome do bucket S3.
        prefix (str): O prefixo dos objetos a serem baixados (pode ser vazio).
        diretorio_local (str): O diretório local para salvar os arquivos baixados.
    """

    s3 = boto3.client('s3')
    total_size = 0
    downloaded_count = 0
    start_time = time.time()

    print(f"Iniciando download de s3://{bucket_name}/{prefix}* para {diretorio_local}...")

    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    file_path = os.path.join(diretorio_local, key)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    download_start_time = time.time()
                    try:
                        s3.download_file(bucket_name, key, file_path)
                        download_end_time = time.time()
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        downloaded_count += 1
                        download_time = download_end_time - download_start_time
                        if download_time > 0:
                            file_rate_mbps = (file_size * 8) / (download_time * 1024 * 1024)
                            print(f"Baixado: {key} ({file_size / (1024 * 1024):.2f} MB) em {download_time:.2f} s ({file_rate_mbps:.2f} Mbps)")
                        else:
                            print(f"Baixado: {key} ({file_size / (1024 * 1024):.2f} MB) em < 0.01 s")

                    except Exception as e:
                        print(f"Erro ao baixar {key}: {e}")

        end_time = time.time()
        tempo_total = end_time - start_time

        if tempo_total > 0 and total_size > 0:
            taxa_bytes_por_segundo = total_size / tempo_total
            taxa_megabits_por_segundo = (taxa_bytes_por_segundo * 8) / (1024 * 1024)
            print("\n--- Resumo do Download ---")
            print(f"Total de arquivos baixados: {downloaded_count}")
            print(f"Tamanho total baixado: {total_size / (1024 * 1024):.2f} MB")
            print(f"Tempo total de download: {tempo_total:.2f} segundos")
            print(f"Taxa de download média: {taxa_megabits_por_segundo:.2f} Mbps")
        else:
            print("Nenhum arquivo encontrado para download ou tempo de download muito curto.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python3 medir_download_boto3_param.py <nome_do_bucket> <prefixo_s3> <diretorio_local>")
        sys.exit(1)

    bucket_name = sys.argv[1]
    prefix = sys.argv[2]
    diretorio_local = sys.argv[3]

    # Certifique-se de que o diretório local existe
    os.makedirs(diretorio_local, exist_ok=True)

    medir_taxa_download_boto3_param(bucket_name, prefix, diretorio_local)
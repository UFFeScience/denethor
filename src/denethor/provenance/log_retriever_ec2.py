import os, json, time, boto3, hashlib
from datetime import datetime, timezone
from typing import Dict
from denethor.core.model.Provider import Provider
from denethor.core.model.WorkflowExecution import WorkflowExecution
from denethor.utils import utils as du
from denethor import constants as const


def retrieve_logs(
    provider: Provider,
    workflow_execution: WorkflowExecution,
    activity_name: str,
    memory: int,
    env_properties: Dict[str, str],
) -> str:
    """
    Retrieves logs from AWS EC2 and saves them to a file.

    Raises:
        ValueError: If no log records were found.

    Returns:
        str: The name of the log file with path.
    """

    log_path = env_properties.get("denethor").get("log.path")
    log_file_name = env_properties.get("denethor").get("log.file")

    log_path = log_path.replace("[provider_tag]", provider.provider_tag)
    log_file_name = log_file_name.replace(
        "[execution_tag]", workflow_execution.execution_tag
    ).replace("[activity_name]", activity_name)

    log_file = os.path.join(log_path, log_file_name)

    start_time_ms = workflow_execution.get_start_time_ms()
    end_time_ms = workflow_execution.get_end_time_ms()



    # !!!!!!!! ATENÇÃO !!!!!!!!!
    # Esse método deve ser implementado para recuperar os logs do EC2
    # Por enquanto, vams assumir que o log já foi recuperado e está no caminho especificado

    # retrieve logs from EC2 instance
    # call retrieve_logs_from_ec2_instance.sh with wetag parameter





    log_file_json = convert_log_to_json(log_file)

    return log_file_json


def convert_log_to_json(file_path: str) -> str:
    """
    Converte um arquivo de log em texto plano para o formato JSON.

    Args:
        file_path (str): Caminho do arquivo de log em texto plano.
    """
    json_logs = []

    # Gera o hash com base no nome do arquivo
    file_name = file_path.split("/")[-1]
    hash_value = hashlib.sha256(
        file_name.encode()
    ).hexdigest()

    with open(file_path, "r") as log_file:
        for line in log_file:
            # Ignora linhas vazias
            if not line.strip():
                continue

            # Divide a linha em três partes: logLevel, timestamp e message
            parts = line.split(" ", 2)  # Divide em no máximo 3 partes
            if len(parts) < 3:
                raise ValueError(f"Formato de log inválido na linha: {line.strip()}")

            p1, p2, p3 = parts  # logLevel, timestamp, message

            # Remove os colchetes do logLevel
            log_level = p1.strip("[]")

            # Converte o timestamp para milissegundos
            try:
                timestamp = int(
                    datetime.strptime(p2, "%Y-%m-%dT%H:%M:%S.%fZ")
                    .replace(tzinfo=timezone.utc)
                    .timestamp() * 1000
                )
            except ValueError:
                raise ValueError(
                    f"Formato de timestamp inválido na linha: {line.strip()}"
                )
            # Verifica se o timestamp é maior que 0
            if timestamp <= 0:
                raise ValueError(
                    f"Timestamp {timestamp} inválido na linha: {line.strip()}"
                )

            # Cria o logStreamName
            date_part = p2.split("T")[0].replace("-", "/")  # Exemplo: "2025/04/03"
            log_stream_name = f"{date_part}/[VM-EC2]{hash_value}"

            # Monta o objeto JSON
            json_logs.append(
                {
                    "logStreamName": log_stream_name,
                    "timestamp": timestamp,
                    "logLevel": log_level,
                    "message": p3.strip(),
                }
            )

    # Define o caminho de saída com a mesma pasta e nome do arquivo de entrada, mas com extensão .json
    output_file = f"{os.path.splitext(file_path)[0]}.json"

    # Salva o resultado em um arquivo JSON
    with open(output_file, "w") as json_file:
        json.dump(json_logs, json_file, indent=4)

    return output_file

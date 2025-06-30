import os, sys, logging


def get_logger(
    execution_tag: str, provider: str, activity: str, env_properties: dict
) -> logging.Logger:

    if not execution_tag or not provider or not activity:
        raise ValueError(
            f"Invalid parameters for get_logger function: execution_tag={execution_tag}, provider={provider}, activity={activity}"
        )

    logger = logging.getLogger(provider + "_" + execution_tag + "_" + activity)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Define o formato do log
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Configuração do formatter personalizado para ISO 8601
        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s.%(msecs)03dZ %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

        log_output_type = env_properties.get(provider).get("log.output_type")

        # Permite que o log seja registrado em um arquivo e/ou na saída padrão

        if "file" in log_output_type:
            log_path = env_properties.get("denethor").get("log.path")
            log_file = env_properties.get("denethor").get("log.file")
            log_file_path = os.path.join(log_path, log_file)

            log_file_path = (
                log_file_path.replace("[provider_tag]", provider)
                .replace("[execution_tag]", execution_tag)
                .replace("[activity_name]", activity)
            )
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        if "stdout" in log_output_type:
            # Se o ambiente for AWS, registra os logs na saída padrão
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

    return logger


def get_simple_logger(file_name: str, file_path: str) -> tuple[logging.Logger, str]:
    """
    Cria um logger simples que registra mensagens em um arquivo e na saída padrão.
    """
    logger = logging.getLogger(file_name)
    logger.setLevel(logging.DEBUG)

    # Define o formato do log
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s.%(msecs)03dZ %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Configuração do arquivo de log
    log_file_path = os.path.join(file_path, file_name)
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Configuração da saída padrão
    # stream_handler = logging.StreamHandler(sys.stdout)
    # stream_handler.setFormatter(formatter)
    # logger.addHandler(stream_handler)

    return logger, log_file_path

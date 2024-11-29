import os, sys, logging

def get_logger(execution_id: str, activity: str, provider: str, env_properties: dict) -> logging.Logger:
    
    logger = logging.getLogger(provider + '_' + execution_id + '_' + activity)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Define o formato do log
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Configuração do formatter personalizado para ISO 8601
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%Z')

        log_path = env_properties.get(provider).get('log.path')
        log_file_name = env_properties.get(provider).get('log.file_name')
        log_output_type = env_properties.get(provider).get('log.output_type')
        
        # Permite que o log seja registrado em um arquivo e/ou na saída padrão
        
        if 'file' in log_output_type:
            file = os.path.join(log_path, log_file_name)
            if execution_id:
                file = file.replace('[execution_id]', execution_id).replace('[activity_name]', activity)
            file_handler = logging.FileHandler(file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        if 'stdout' in log_output_type:
            # Se o ambiente for AWS, registra os logs na saída padrão
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

    return logger
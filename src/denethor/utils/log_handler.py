import sys, logging

def get_logger(execution_id: str, activity_name: str, execution_env: dict) -> logging.Logger:
    
    logger = logging.getLogger(execution_env.get('env_name')+'_'+execution_id+'_'+activity_name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Define o formato do log
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Configuração do formatter personalizado para ISO 8601
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%Z')

        log_params = execution_env.get('log_params')
        output_type = log_params.get('output_type')
        
        # Permite que o log seja registrado em um arquivo e/ou na saída padrão
        
        if 'file' in output_type:
            file = log_params.get('path')+'/'+log_params.get('file_name')
            if execution_id:
                file = file.replace('[execution_id]', execution_id).replace('[activity_name]', activity_name)
            file_handler = logging.FileHandler(file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        if 'stdout' in output_type:
            # Se o ambiente for AWS, registra os logs na saída padrão
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

    return logger
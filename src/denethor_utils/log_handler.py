import logging

def get_logger(execution_env: dict) -> logging.Logger:
    
    logger = logging.getLogger(execution_env.get('env_name'))
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Define o formato do log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        log_output = execution_env.get('log_output')
        if log_output == 'file':
            file = execution_env.get('log_path')+'/my_log.log'
            file_handler = logging.FileHandler(file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        elif log_output == 'stdout':
            # Se o ambiente for AWS, registra os logs na saída padrão
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

    return logger
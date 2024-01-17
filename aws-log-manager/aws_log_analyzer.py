from db.db_model import *
from db.repository import *
from db.conn import Connection
from utils.request_log_dto import RequestLogDTO
import json
import re


def main():

    # abrindo o arquivo com os logs da AWS salvos no formato json
    with open('aws-log-manager/_logs/logs_tree_constructor.json') as f:
        data = f.readlines()

    request_id_dict = {}

    # iterando sobre todo o conjunto de logs recuperados para separar por request_id
    for line in data:
        log_item = json.loads(line)
        message = log_item.get('message')
        if message:
            encoded_message = message.encode('utf-8', 'ignore').decode('utf-8')
            # se a mensagem do log possuir a tag RequestId -> armazenar no dicionário
            if "RequestId" in encoded_message:
                request_id = re.search('RequestId: (.+?)\\s', message).group(1)
                if request_id not in request_id_dict:
                    request_id_dict[request_id] = []
                request_id_dict[request_id].append(log_item)
    
    # iterando sobre o conjunto de logs de um request_id (cada chamda da função lambda)
    # esse conjunto representa uma execução completa da atividade "tree_constructor" para um arquivo de entrada
    for request_id, log_items in request_id_dict.items():
        request_log = RequestLogDTO(request_id)
        for log_item in log_items:
            request_log.process(log_item)
        
        request_log.print()   
        save_to_database(request_log)

    # log_str = json.dumps(log)
    


def save_to_database(req : RequestLogDTO):
    
    print(f"--------------------------------------------")
    print(f'Saving Execution info to Database...')
    print(f"--------------------------------------------")
    session = Connection().get_session()
   
    # Instânciando as classes de repositórios
    file_repo = FileRepository(session)
    service_provider_repo = ServiceProviderRepository(session)
    workflow_activity_repo = WorkflowActivityRepository(session)
    service_execution_repo = ServiceExecutionRepository(session)


    # Buscando no banco os dados básicos do modelo (dados pré-existentes)
    service_provider = service_provider_repo.get_by_attributes({'name': 'AWS Lambda'})
    workflow_activity = workflow_activity_repo.get_by_attributes({'name': 'tree_constructor'})

    
    # verificar se os registros presentes no Log já estão cadastrados na base
    # caso positivo -> apenas recupera o registro
    # caso negativo -> realiza a inclusão e retorna o novo registro
    
    # arquivo "consumido" pela atividade
    consumed_file_data = {
        'name': req.consumed_file_name,
        'size': req.consumed_file_size,
        'path': req.consumed_file_path,
        'bucket': req.consumed_file_bucket
    }
    consumed_file, created = file_repo.get_or_create(consumed_file_data)
    print(f'{'Saving' if created else 'Retrieving'} Consumed File info: {consumed_file}')

    # arquivo "produzido" pela atividade
    produced_file_data = {
        'name': req.produced_file_name,
        'size': req.produced_file_size,
        'path': req.produced_file_path,
        'bucket': req.produced_file_bucket
    }
    produced_file, created = file_repo.get_or_create(produced_file_data)
    print(f'{'Saving' if created else 'Retrieving'} Produced File info: {produced_file}')


    # estatísticas da execução do serviço
    service_execution_data = {
        'request_id': req.request_id,
        'log_stream_name': req.log_stream_name,
        'start_time': req.get_start_time_as_date(),
        'end_time': req.get_end_time_as_date(),
        'duration': req.duration,
        'billed_duration': req.billed_duration,
        'init_duration': req.init_duration,
        'consumed_file_download_duration': req.consumed_file_download_duration,
        'produced_file_upload_duration': req.produced_file_upload_duration,
        'memory_size': req.memory_size,
        'max_memory_used': req.max_memory_used,
        'error_message': '',
        'activity_id': workflow_activity.id,
        'service_id': service_provider.id,
        'consumed_file_id': consumed_file.id,
        'produced_file_id': produced_file.id
    }
    
    service_execution, created = service_execution_repo.get_or_create(service_execution_data)
    print(f'{'Saving' if created else 'Retrieving'} Service Execution info: [{service_execution.id}]={workflow_activity.name} ({service_execution.duration} ms)')

    print(f'Finished saving Service Execution info to Database: [{service_execution.id}]={workflow_activity.name}')
    print(f'\n\n')

if __name__ == "__main__":
    main()
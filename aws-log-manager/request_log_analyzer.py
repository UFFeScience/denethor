from db.db_model import *
from db.repository import *
from db.conn import Connection
from utils.request_log_model import RequestLogModel
import json
import re

# Define the list of keywords for filtering
# keywords = ["RequestId:"]  # Add your keywords here
# keywords = ["INIT", "START", "s3_bucket", "s3_key", "END:", "REPORT"]  # Add your keywords here


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
        request_log = RequestLogModel(request_id)
        for log_item in log_items:
            request_log.process(log_item)
        
        request_log.print()   
        save_to_database(request_log)

    # log_str = json.dumps(log)
    


def save_to_database(req : RequestLogModel):
    
    print(f"--------------------------------------------")
    print(f'Saving Execution info to Database...')
    print(f"--------------------------------------------")
    session = Connection().get_session()
   
    # Instânciando as classes de repositórios
    file_repo = FileRepository(session)
    statistics_repo = StatisticsRepository(session)
    service_provider_repo = ServiceProviderRepository(session)
    workflow_activity_repo = WorkflowActivityRepository(session)
    service_execution_repo = ServiceExecutionRepository(session)
    execution_statistics_repo = ExecutionStatisticsRepository(session)


    # Buscando no banco os dados básicos do modelo (dados pré-existentes)
    service_provider = service_provider_repo.get_by_name(name='AWS Lambda')
    workflow_activity = workflow_activity_repo.get_by_name(name='tree_constructor')
    upload_duration_statistics   = statistics_repo.get_by_name(name='upload_duration')
    download_duration_statistics = statistics_repo.get_by_name(name='download_duration')

    
    # verificar se os arquivos presentes no registro de Log já estão cadastrados na base
    # caso positivo -> apenas recuperar seus ids
    # caso negativo -> realizar a inclusão antes
    
    # arquivo "consumido" pela atividade
    consumed_file_data = {
        'name': req.download_file_name,
        'size': req.download_file_size,
        'path': req.download_file_path
    }
    consumed_file = file_repo.get_by_attributes(consumed_file_data)
    if not consumed_file:
        consumed_file = file_repo.create(consumed_file_data)
        print(f'Saving Consumed File info: {consumed_file}')


    # arquivo "produzido" pela atividade
    produced_file_data = {
        'name': req.upload_file_name,
        'size': req.upload_file_size,
        'path': req.upload_file_path
    }
    produced_file = file_repo.get_by_attributes(produced_file_data)
    if not produced_file:
        produced_file = file_repo.create(produced_file_data)
        print(f'Saving Produced File info: {produced_file}')

    
   
    # incluir as estatísticas em service_execution
    service_execution_data = {
        'start_time': req.start_time_date(),
        'end_time': req.end_time_date(),
        'duration': req.duration,
        'error_message': '',
        'activity_id': workflow_activity.id,
        'service_id': service_provider.id,
        'consumed_file_id': consumed_file.id,
        'produced_file_id': produced_file.id
    }
    service_execution = service_execution_repo.get_by_attributes(service_execution_data)
    if not service_execution:
        service_execution = service_execution_repo.create(service_execution_data)
        print(f'Saving Service Execution info: [{service_execution.id}]={workflow_activity.name} ({service_execution.duration} ms)')


    # incluir as estatísticas extras em execution_statistics
    # upload_duration
    execution_statistics_upload_data = {
        'value_float': req.upload_duration,
        'service_execution_id': service_execution.id,
        'statistics_id': upload_duration_statistics.id
    }
    execution_statistics_upload = execution_statistics_repo.get_by_attributes(execution_statistics_upload_data)
    if not execution_statistics_upload:
        execution_statistics_upload = execution_statistics_repo.create(execution_statistics_upload_data)
        print(f'Saving Upload Execution Statistics info: [{execution_statistics_upload.id}]')

    # download_duration
    execution_statistics_download_data = {
        'value_float': req.download_duration,
        'service_execution_id': service_execution.id,
        'statistics_id': download_duration_statistics.id
    }
    execution_statistics_download = execution_statistics_repo.get_by_attributes(execution_statistics_download_data)
    if not execution_statistics_download:
        execution_statistics_download = execution_statistics_repo.create(execution_statistics_download_data)
        print(f'Saving Download Execution Statistics info: [{execution_statistics_download.id}]')


    print(f'Finished saving Service Execution info to Database: [{service_execution.id}]={workflow_activity.name}')
    print(f'\n\n')

if __name__ == "__main__":
    main()
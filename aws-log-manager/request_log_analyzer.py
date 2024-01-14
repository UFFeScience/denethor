from db.db_model import *
from db.repository import *
from db.conn import Connection
from utils import util
from utils.request_log_model import RequestLogModel
import json
import re

# Define the list of keywords for filtering
# keywords = ["RequestId:"]  # Add your keywords here
# keywords = ["INIT", "START", "s3_bucket", "s3_key", "END:", "REPORT"]  # Add your keywords here


def main():

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
    
    # iterando sobre todos os logs de um request_id para organizar os logs de uma execução 
    # completa de tree_constructor
    for request_id, log_items in request_id_dict.items():
        request_log = RequestLogModel(request_id)
        for log_item in log_items:
            request_log.process(log_item)
        
        request_log.print()   
        
    save_to_database(request_log)

    # log_str = json.dumps(log)
    


if __name__ == "__main__":
    main()

def save_to_database(req : RequestLogModel):
    
    session = Connection().get_session()
   
    # Instânciando as classes de repositórios
    file_repo = FileRepository(session)
    statistics_repo = StatisticsRepository(session)
    service_provider_repo = ServiceProviderRepository(session)
    workflow_activity_repo = WorkflowActivityRepository(session)
    service_execution_repo = ServiceExecutionRepository(session)

    # Buscando no banco os dados básicos da execução
    provider = service_provider_repo.get_by_name(name='AWS Lambda')
    activity = workflow_activity_repo.get_by_name(name='tree_constructor')
    stat_up   = statistics_repo.get_by_name(name='upload_duration')
    stat_down = statistics_repo.get_by_name(name='download_duration')

    # Verificando se os arquivos presentes no registro de Log estão cadastrados na base
    # Caso positivo, apenas recuperar seus ids
    # Caso negativo, realizar a inclusão antes
    consumed_file = file_repo.get_by_name_and_path(req.download_file_name, req.download_file_path)
    if not consumed_file:
        new_consumed_file = File(
            name=req.download_file_name,
            size=req.download_file_size,
            path=req.download_file_path)
        consumed_file = file_repo.create(new_consumed_file)

    produced_file = file_repo.get_by_name_and_path(req.upload_file_name, req.upload_file_path)
    if not produced_file:
        new_produced_file = File(
            name=req.upload_file_name,
            size=req.upload_file_size,
            path=req.upload_file_path)
        produced_file = file_repo.create(new_produced_file)
    
    
    # Incluir as estatísticas em service_execution
    new_service_execution = ServiceExecution(
        start_time="2024-01-13 10:00:00",
        end_time="2024-01-13 11:00:00",
        duration=3600,
        error_message="Some error",
        activity_id=2,
        service_id=3,
        consumed_file_id=4,
        produced_file_id=5
)


    # Incluir as estatísticas extras em execution_statistics
    # upload_duration e download_duration

from log_utils import *
from request_log_model import RequestLogModel

# Define the list of keywords for filtering
# keywords = ["RequestId:"]  # Add your keywords here
# keywords = ["INIT", "START", "s3_bucket", "s3_key", "END:", "REPORT"]  # Add your keywords here


def main():

    with open('aws-log-manager/logs/logs_tree_constructor.json') as f:
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
    
    # iterando sobre todos os logs de um request_id
    for request_id, log_items in request_id_dict.items():
        request_log = RequestLogModel(request_id)
        for log_item in log_items:
            request_log.process(log_item)
        
        request_log.print()
        
        
        
    # request_analyzer.save_to_database()

    # log_str = json.dumps(log)
    


if __name__ == "__main__":
    main()
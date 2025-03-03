import re


# Filters and organizes log records by RequestId
# Each set represents a complete execution of the activity for a set of input files
def group_logs_by_request(logs: dict) -> dict:

    # Dicionário para armazenar os logs filtrados
    logs_by_request = {}

    # Loop através dos logs
    for log in logs:
        # Obter o RequestId do log
        request_id = get_request_id(log["message"])

        # Se o RequestId não for None, adicione o log ao dicionário
        if request_id is not None:
            if request_id not in logs_by_request:
                logs_by_request[request_id] = []
            logs_by_request[request_id].append(log)

    return logs_by_request


def get_request_id(log_message):
    match = re.search("RequestId: (\\S+)", log_message)
    request_id = match.group(1) if match else None
    return request_id

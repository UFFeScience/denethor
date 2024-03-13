import boto3
import time

def monitor_lambda_execution(params):

    function_name = params['functionName']
    requests = params['invoke_lambda_execution'].get(f'{function_name}_requests', [])
    
    if requests == []: 
        raise ValueError(f'No requests to monitor for function {function_name}')

    lambda_client = boto3.client('lambda')
    completed_requests = {}  # Dicionário para armazenar o estado dos requests

    files = params['dataFiles']['files']

    if function_name == 'tree_constructor':
        if len(files) <= 2:
            time.sleep(5)
        elif len(files) <= 10:
            time.sleep(60)
        else:
            time.sleep(3*60)
    elif function_name == 'subtree_mining':
        if len(files) <= 2:
            time.sleep(15)
        elif len(files) <= 10:
            time.sleep(5*60)
        else:
            time.sleep(16*60)
        
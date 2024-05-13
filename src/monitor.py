import boto3
import time
from invoker import LOCAL_WIN, LAMBDA, VM_LINUX

def monitor_execution(params):

    execution_env = params.get('step_params').get('execution_env')

    if execution_env == LOCAL_WIN:
        return monitor_local_execution(params)

    elif execution_env == LAMBDA:
        return monitor_lambda_execution(params)

    else:
        raise ValueError(f'Invalid execution environment: {execution_env}')


def monitor_lambda_execution(params):

    activity_name = params.get('step_params').get('activity')
    requests = params.get('produced_data').get(f'{activity_name}_requests', [])
    
    if not requests: 
        raise ValueError(f'No requests to monitor for function {activity_name}')

    lambda_client = boto3.client('lambda')
    completed_requests = {}  # Dicionário para armazenar o estado dos requests

    datasets = params.get('datasets')

    if activity_name == 'tree_constructor':
        if len(datasets) <= 2:
            time.sleep(1)
        elif len(datasets) <= 10:
            time.sleep(2)
        else:
            time.sleep(10)
    elif activity_name == 'subtree_mining':
        if len(datasets) <= 2:
            time.sleep(15)
        elif len(datasets) <= 10:
            time.sleep(2*60)
        else:
            time.sleep(16*60)

def monitor_local_execution(params):

    time.sleep(1)
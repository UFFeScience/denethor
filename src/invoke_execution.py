import boto3
import json
import importlib
import sys
from utils import utils



# Invokes a Lambda function execution based on the provided parameters.
def invoke_lambda_execution(params):
    base_payload = {
        'inputBucket': params['inputBucket'],
        'inputKey': params['inputKey'],
        'outputBucket': params['outputBucket'],
        'outputKey': params['outputKey']
    }

    files = params['input_files_name']
    execution_strategy = params['execution_strategy']
    function_name = params['function_name']
    
    requests = []

    if execution_strategy == 'for_each_input':
        for file_name in files:
            payload = base_payload | {'file': file_name}
            request_id = invoke_async(function_name, payload)
            requests.append(request_id)
            print(f'{function_name} triggered with payload {payload} with execution strategy {execution_strategy} for file: {file_name}')

    elif execution_strategy == 'for_all_inputs':
        payload = base_payload | {'files': files}
        request_id = invoke_async(function_name, payload)
        requests.append(request_id)
        print(f'{function_name} triggered with payload {payload} with execution strategy {execution_strategy} for files: {files}')
    
    else:
        raise ValueError(f'Invalid execution strategy: {execution_strategy}')
    
    return {f"{function_name}_requests" : requests}


def invoke_async(function_name, payload):
    """
    Invokes a Lambda function asynchronously with the given function name and payload.

    Parameters:
    - function_name (str): The name of the Lambda function to invoke.
    - payload (dict): The payload to pass to the Lambda function.

    Returns:
    - str: The request ID of the Lambda function invocation.
    """
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
                function_name=function_name,
                InvocationType='Event',
                Payload=json.dumps(payload)
            )
    request_id = response['ResponseMetadata']['RequestId']
    return request_id


def invoke_local_execution(params):
    
    step_params = params.get('step_params')

    # function_name = 'handler' # nome da função padrão dentro da implementação da atividade
    # execution_strategy = step_params.get('execution_strategy')

    # env_name = step_params.get('execution_env')
    
    env_config = params.get('execution_env_config')
    files = params.get('input_files')

    
    
    # all_requests = []
    # all_produced_files = []
    result_set= []
    # Get the python function from the module
    
    if execution_strategy == 'for_each_input':
        for file in files:
            payload = {
                'input_file': file,
                'subtree_matrix': subtree_matrix, # para a etapa do maf_database_create
                'env_name': env_name,
                'env_config': env_config
                }

            # Call the python function with the specified parameters and return the request ID
            result = utils.invoke_python(module_name, module_path, function_name, payload, None)
            # all_requests.append(request_id)
            # all_produced_files.append(produced_files)
            result_set.append(result)
            print(f'{activity_name} triggered with payload {payload} with execution strategy {execution_strategy} for file: {file}')

    elif execution_strategy == 'for_all_inputs':
        payload = {
            'input_files': files,
            'subtree_matrix': subtree_matrix, # para a etapa do maf_database_create
            'env_name': env_name,
            'env_config': env_config
            }
        # Call the python function with the specified parameters and return the request ID
        result = utils.invoke_python(module_name, module_path, function_name, payload, None)
        # all_requests.append(request_id)
        # all_produced_files.append(produced_files)
        result_set.append(result)
        print(f'{activity_name} triggered with payload {payload} with execution strategy {execution_strategy} for files: {files}')
    
    else:
        raise ValueError(f'Invalid execution strategy: {execution_strategy}')
    
    
    return result_set
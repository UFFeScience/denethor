import boto3
import json
import importlib
import sys
from utils import utils


def invoke_execution(params):
    """
    Invokes a function execution based on the provided parameters.

    Args:
        params (dict): A dictionary containing the following keys:
    """
    
    if params.get('step_params').get('env_name') == 'LOCAL_WIN':
        return invoke_local_execution(params)

    elif params.get('step_params').get('env_name') == 'LAMBDA':
        return invoke_lambda_execution(params)

    
    else:
        raise ValueError(f'Invalid execution environment: {params.get('step_params').get('env_name')}')


def invoke_lambda_execution(params):
    """
    Invokes a Lambda function execution based on the provided parameters.

    Args:
        params (dict): A dictionary containing the following keys:
            - inputBucket (str): The input bucket name.
            - inputKey (str): The input key.
            - outputBucket (str): The output bucket name.
            - outputKey (str): The output key.
            - dataFiles (dict): A dictionary containing the following keys:
                - files (list): A list of file names.
            - execution_strategy (str): The execution strategy. Can be either 'for_each_file' or 'for_all_files'.
            - function_name (str): The name of the Lambda function.

    Returns:
        dict: A dictionary containing the function name appended with "_requests" as the key and a list of request IDs as the value.

    Raises:
        ValueError: If an invalid execution strategy is provided.

    """
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

    if execution_strategy == 'for_each_file':
        for file_name in files:
            payload = base_payload | {'file': file_name}
            request_id = invoke_async(function_name, payload)
            requests.append(request_id)
            print(f'{function_name} triggered with payload {payload} with execution strategy {execution_strategy} for file: {file_name}')

    elif execution_strategy == 'for_all_files':
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

    activity_name = step_params.get('activity')
    function_name = 'handler' # nome da função padrão dentro da implementação da atividade
    execution_strategy = step_params.get('execution_strategy')
    module_name = step_params.get('activity_module_name')
    module_path = step_params.get('activity_module_path')
    env_name = step_params.get('env_name')
    env_conf = params.get('all_env_conf').get(env_name)
    datasets = params.get('datasets')

    requests = []
    # Get the python function from the module
    
    if execution_strategy == 'for_each_file':
        for dataset in datasets:
            payload = {
                'file': dataset,
                'env_name': env_name,
                'env_conf': env_conf,
                'request_id': utils.generate_request_id()
                }

            # Call the python function with the specified parameters and return the request ID
            request_id = utils.invoke_python(module_name, module_path, function_name, payload, None)
            requests.append(request_id)
            print(f'{activity_name} triggered with payload {payload} with execution strategy {execution_strategy} for file: {dataset}')

    elif execution_strategy == 'for_all_files':
        payload = {
            'files': datasets,
            'env_conf': env_conf,
            }
        # Call the python function with the specified parameters and return the request ID
        request_id = utils.invoke_python(module_name, module_path, function_name, payload, None)
        requests.append(request_id)
        print(f'{activity_name} triggered with payload {payload} with execution strategy {execution_strategy} for files: {datasets}')
    
    else:
        raise ValueError(f'Invalid execution strategy: {execution_strategy}')
    
    return {f"{activity_name}_requests" : requests}
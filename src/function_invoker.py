import boto3
import json

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
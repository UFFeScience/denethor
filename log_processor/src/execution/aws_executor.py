import boto3
import json
import importlib
import sys

# params = {
#     'execution_id': execution_id,
#     'start_time_ms': start_time_ms,
#     'end_time_ms': end_time_ms,
#     'activity': activity,
#     'execution_env': execution_env,
#     'strategy': strategy,
#     'input_data': input_data,
#     'output_param': output_param,
# }

# Invokes a Lambda function execution based on the provided parameters.
def execute(params):

    payload = {
        'input_bucket': params['input_bucket'],
        'input_key': params['input_key'],
        'output_bucket': params['output_bucket'],
        'output_key': params['output_key'], 
        'execution_data': params['execution_data']
    }

    execution_data = params['execution_data']
    function_name = params['function_name']
    
    requests = []

    request_id = invoke_async(function_name, payload)
    requests.append(request_id)
    print(f'{function_name} triggered with payload {payload} with execution strategy {execution_strategy} for file: {file_name}')

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
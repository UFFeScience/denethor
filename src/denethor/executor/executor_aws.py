import boto3, json

# payload = {
#     'execution_id': execution_id,
#     'start_time_ms': start_time_ms,
#     'end_time_ms': end_time_ms,
#     'activity': activity,
#     'execution_env': execution_env,
#     'configuration_id' : configuration_id,
#     'strategy': strategy,
#     'input_data': input_data,
#     'all_input_data': all_input_data,
#     'output_param': output_param,
# }

def execute(payload):
    """
    Executes the activity in the AWS Lambda environment based on the provided parameters.
    """
    activity_name = payload.get('activity')
    configuration_id = payload.get('configuration_id')
    
    response_data = invoke_lambda(activity_name, configuration_id, payload, 350)
    return response_data


def invoke_lambda(function_name, configuration_id, payload, timeout=120, async_invoke=False):
    """
    Invokes a Lambda function with the given function name and payload.

    Parameters:
    - function_name (str): The name of the Lambda function to invoke.
    - configuration_id (int): The configuration for the Lambda function.
    - payload (dict): The payload to pass to the Lambda function.
    - async_invoke (bool): Whether to invoke the function asynchronously. Default is False.
    - timeout (int): The timeout for the request in seconds. Default is 120 seconds.

    Returns:
    - str: The request ID of the Lambda function invocation.
    - dict (optional): The response payload if invoked synchronously.
    """
    
    iteration_info = ""
    if payload.get('iteration'):
        iteration_info = f" | iteration={payload.get('iteration')}..{len(payload.get('all_input_data'))}"

    function_to_invoke = function_name + '_' + configuration_id
    print(f"\n>>> Invoking Lambda Function: {function_to_invoke} | timeout={timeout} | async_invoke={async_invoke}" + iteration_info)
    

    lambda_client = boto3.client('lambda', config=boto3.session.Config(read_timeout=timeout))
    invocation_type = 'Event' if async_invoke else 'RequestResponse'
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType=invocation_type,
        Payload=json.dumps(payload)
    )
    
    print(f">>> Lambda function {function_name} invoked successfully!")
    
    if async_invoke:
        return response['ResponseMetadata']['RequestId']
    else:
        return json.loads(response['Payload'].read())
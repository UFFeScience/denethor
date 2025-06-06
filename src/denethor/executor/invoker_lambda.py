from typing import Dict
import boto3, json


def invoke(
    function_name: str,
    memory: int,
    timeout: int,
    async_invoke: bool,
    payload: Dict[str, str],
):
    """
    Invokes a AWS Lambda function with the given function name and payload.

    Parameters:
    - function_name (str): The name of the Lambda function to invoke.
    - memory (int): The memory allocated for the Lambda function execution.
    - timeout (int): The timeout for the request in seconds.
    - async_invoke (bool): Whether to invoke the function asynchronously.
    - payload (dict): The payload to pass to the Lambda function.

    Returns:
    - str: The request ID of the Lambda function invocation.
    - dict (optional): The response payload if invoked synchronously.
    """

    function_to_invoke = function_name + "_" + str(memory)
    print(
        f">>> Invoking Lambda Function: {function_to_invoke} | timeout: {timeout} | async: {async_invoke}"
    )

    if payload.get("index_data"):
        print(
            f">>> index_data={payload.get('index_data')}..{len(payload.get('input_data'))-1}"
        )

    lambda_client = boto3.client(
        "lambda", config=boto3.session.Config(read_timeout=timeout)
    )
    invocation_type = "Event" if async_invoke else "RequestResponse"
    
    # print(f"\n {json.dumps(payload)}")
    
    response = lambda_client.invoke(
        FunctionName=function_to_invoke,
        InvocationType=invocation_type,
        Payload=json.dumps(payload),
    )

    if response["StatusCode"] == 200:
        payload_response = json.loads(response["Payload"].read())
        if "FunctionError" in response:
            raise Exception(
                f"Function error: {response['FunctionError']}, {payload_response}"
            )
    
    elif response["StatusCode"] == 400:
        raise Exception(f"Bad Request: {response}")
    
    elif response["StatusCode"] == 403:
        raise Exception(f"Forbidden: {response}")
    
    elif response["StatusCode"] == 500:
        raise Exception(f"Internal Server Error: {response}")
    
    else:
        raise Exception(f"Error invoking Lambda function: {response}")

    print(f"\n>>> Lambda function {function_to_invoke} invoked successfully!")
    # print(f"\n>>> Payload: {payload_response}")

    if async_invoke:
        return response["ResponseMetadata"]["RequestId"]
    else:
        return payload_response

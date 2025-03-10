from typing import Dict
import boto3, json


def invoke(
    instance_id: str,
    key_path: str,
    module_identifier: str,
    module_path: str,
    target_method: str,
    payload: Dict[str, str],
):
    """
    Invokes a AWS EC2 instance with the given instance ID and payload.

    Parameters:
    - instance_id (str): The ID of the EC2 instance to invoke.
    - key_path (str): The path to the private key file to use for SSH authentication.
    - module_identifier (str): The name of the module containing the target method to execute on the EC2 instance.
    - module_path (str): The path to the script to execute on the EC2 instance.
    - payload (dict): The payload to pass to the EC2 instance

    Returns:
    - str: The request ID of the EC2 instance invocation.
    - dict (optional): The response payload.
    """

    print(f">>> Invoking EC2 Instance: {instance_id} | module_path: {module_path} | module_identifier: {module_identifier} | key_path: {key_path}")

    print(f"\n {json.dumps(payload)}")

    if payload.get("index_data"):
        print(
            f">>> index_data={payload.get('index_data')}..{len(payload.get('input_data'))-1}"
        )
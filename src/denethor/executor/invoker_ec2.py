import os
from typing import Dict
import paramiko
import json


def invoke(
    instance_dns: str,
    ec2_user: str,
    key_path: str,
    ec2_path: str,
    module_path: str,
    module_identifier: str,
    target_method: str,
    payload: Dict[str, str],
):
    """
    Invokes a AWS EC2 instance with the given instance ID and payload.

    Parameters:
    - instance_dns (str): The DNS of the EC2 instance to invoke.
    - ec2_user (str): The username to use for SSH authentication.
    - key_path (str): The path to the private key file to use for SSH authentication.
    - ec2_path (str): The path to the script to execute on the EC2 instance.
    - module_path (str): The path to the script to execute on the EC2 instance.
    - module_identifier (str): The name of the module containing the target method to execute on the EC2 instance.
    - target_method (str): The name of the method to call in the module.
    - payload (dict): The payload to pass to the EC2 instance

    Returns:
    - str: The request ID of the EC2 instance invocation.
    - dict (optional): The response payload.
    """

    print(
        f">>> Invoking EC2 Instance: {instance_dns} | module_path: {module_path} | module_identifier: {module_identifier} | key_path: {key_path}"
    )

    print(f"\n {json.dumps(payload)}")

    if payload.get("index_data"):
        print(
            f">>> index_data={payload.get('index_data')}..{len(payload.get('input_data'))-1}"
        )

    # Convert payload to JSON
    payload_json = json.dumps(payload)

    # Establish SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(instance_dns, username=ec2_user, key_filename=key_path)

    # TODO: Ajustar o comando para invocar o script na instância EC2
    command = " "

    # Execute the command on the EC2 instance
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()

    # Close the SSH connection
    ssh.close()

    if error:
        raise Exception(f"Error: {error}")
    
    print(output)

    return output

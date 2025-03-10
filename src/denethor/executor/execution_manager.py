import json
import os
from typing import List, Dict, Optional
from denethor.executor import invoker_lambda, invoker_local, invoker_ec2
from denethor import constants as const


def execute_activity(
    execution_tag: str,
    provider_tag: str,
    strategy: str,
    activity: str,
    previous_activity: str,
    memory: int,
    input_data: List[str],
    env_properties: Dict[str, str],
) -> List[Dict[str, str]]:
    """
    Executes the activity by provider and strategy and returns the results.
    Parameters:
    - execution_tag (str): The TAG of the execution.
    - provider_tag (str): The provider TAG for the execution environment.
    - strategy (str): The execution strategy for the activity.
    - activity (str): The name of the activity to execute.
    - previous_activity (str): The name of the previous activity.
    - memory (int): The memory allocated for the activity execution.
    - input_data (list): The complete input data for the activity execution.
    - env_properties (dict): The properties of the execution environment.

    Returns:
    - list: The results of the activity execution as a list of dictionaries.

    Return example:
    {'request_id': 'uuid_2a29bdff_3d29_46fa_b1bd_7d6779865002', 'produced_data': ['tree_ORTHOMCL1.nexus']}
    {'request_id': 'uuid_dc71e784_52ca_428d_8bde_433ed7b0f5b6', 'produced_data': ['tree_ORTHOMCL256.nexus']}
    """

    # Validation of input data
    if input_data is None:
        raise ValueError(
            f"Invalid input data={input_data} for Execution Manager of activity={activity}"
        )

    print(
        f"\n>>>Execution Manager: {activity} | strategy:={strategy} | input_data:={input_data}"
    )

    results = []

    if strategy == const.FOR_EACH_INPUT:
        for index_data in range(len(input_data)):
            result = execute_by_provider(
                execution_tag,
                provider_tag,
                activity,
                previous_activity,
                memory,
                input_data,
                index_data,
                env_properties,
            )
            results.append(result)

    elif strategy == const.FOR_ALL_INPUTS:
        result = execute_by_provider(
            execution_tag,
            provider_tag,
            activity,
            previous_activity,
            memory,
            input_data,
            None,
            env_properties,
        )
        results.append(result)

    else:
        raise ValueError(f"Invalid strategy={strategy} for activity={activity}")

    return results


# Execute the activity by provider
def execute_by_provider(
    execution_tag: str,
    provider: str,
    activity: str,
    previous_activity: str,
    memory: int,
    input_data: List[Dict],
    index_data: Optional[int],
    env_properties: Dict[str, str],
) -> Dict[str, str]:

    payload = {
        "execution_tag": execution_tag,
        "provider": provider,
        "activity": activity,
        "previous_activity": previous_activity,
        "input_data": input_data,
        "index_data": index_data,
        "env_properties": env_properties,
    }

    print(f"\n>>> Payload: {json.dumps(payload)}")

    if provider == const.LOCAL:
        module_identifier = activity
        module_path = env_properties.get(provider).get("path.src")
        target_method = env_properties.get(provider).get("target_method")
        return invoker_local.invoke(
            module_identifier, module_path, target_method, payload
        )

    elif provider == const.AWS_EC2:
        instance_id = os.getenv('instance-id')
        key_path = os.getenv('key-pair-path')
        module_identifier = activity
        module_path = env_properties.get(provider).get("path.src")
        ec2_base_path = os.getenv("ec2-base-path")
        module_path = os.path.join(ec2_base_path, module_path)
        target_method = env_properties.get(provider).get("target_method")
        return invoker_ec2.invoke(
            instance_id,
            key_path,
            module_identifier,
            module_path,
            target_method,
            payload,
        )

    elif provider == const.AWS_LAMBDA:
        return invoker_lambda.invoke(activity, memory, payload)

    else:
        raise ValueError(
            f"Invalid execution provider={provider} for activity={activity}"
        )

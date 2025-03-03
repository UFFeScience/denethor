from typing import List, Dict, Optional
from denethor.executor import invoker_aws, invoker_local
from denethor.environments import *

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

    if provider_tag not in ExecutionProviderEnum.__members__:
        raise ValueError(
            f"Invalid execution provider={provider_tag} for Execution Manager of activity={activity}"
        )
    
    if strategy not in ExecutionStrategyEnum.__members__:
        raise ValueError(
            f"Invalid execution strategy={strategy} for Execution Manager of activity={activity}"
        )
    
    if memory not in MemoryConfigurationEnum.__members__:
        raise ValueError(
            f"Invalid memory configuration={memory} for Execution Manager of activity={activity}"
        )

    print(
        f"\n>>>Execution Manager: {activity} | strategy:={strategy} | input_data:={input_data}"
    )

    results = []

    if strategy == ExecutionStrategyEnum.FOR_EACH_INPUT:
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

    elif strategy == ExecutionStrategyEnum.FOR_ALL_INPUTS:
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
        "execution_id": execution_tag,
        "provider": provider,
        "activity": activity,
        "previous_activity": previous_activity,
        "input_data": input_data,
        "index_data": index_data,
        "env_properties": env_properties,
    }

    if provider == ExecutionProviderEnum.LOCAL:
        src_path = env_properties.get(provider).get("path.src")
        return invoker_local.invoke_local_python(activity, src_path, "handler", payload)

    elif provider == ExecutionProviderEnum.AWS_LAMBDA:
        return invoker_aws.invoke_aws_lambda(activity, memory, payload)

    else:
        raise ValueError(
            f"Invalid execution provider={provider} for activity={activity}"
        )

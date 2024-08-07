from denethor_executor import executor_local, executor_aws
from denethor_utils.env import LOCAL, AWS_LAMBDA, VM_LINUX

def execute(params):
    """
    Executes the activity based on the provided parameters.
    Parameters:
    - params (dict): The parameters for the activity execution, containing the following keys:
        - execution_id (str): The ID of the execution.
        - start_time_ms (int): The start time of the execution in milliseconds.
        - end_time_ms (int): The end time of the execution in milliseconds.
        - action (str): The name of the action to execute.
        - activity (str): The name of the activity to execute.
        - execution_env (dict): The execution environment configuration.
        - strategy (str): The execution strategy for the activity.
        - all_input_data (list): The complete input data for the activity execution.

    Returns:
    - list: The results of the activity execution as a list of dictionaries.
    
    Example: 
    {'request_id': 'uuid_2a29bdff_3d29_46fa_b1bd_7d6779865002', 'produced_data': ['tree_ORTHOMCL1.nexus']}
    {'request_id': 'uuid_dc71e784_52ca_428d_8bde_433ed7b0f5b6', 'produced_data': ['tree_ORTHOMCL256.nexus']}
    """

    action = params.get('action')
    activity_name = params.get('activity')
    strategy = params.get('strategy')
    all_input_data = params.get('all_input_data')
    
    print(f"\n>>> Action *{action}* activity *{activity_name}* triggered with execution strategy: *{strategy}* for input data: {all_input_data}")

    results = []
    
    if action != 'execute':
        raise ValueError(f"Invalid action: {action}")
    
    if strategy == 'for_each_input':
        i = 0
        for input in all_input_data:
            i += 1
            params['iteration'] = i
            params['input_data'] = input
            params['all_input_data'] = all_input_data
            result = execute_by_env(params)
            results.append(result)

    elif strategy == 'for_all_inputs':
        params['input_data'] = all_input_data
        result = execute_by_env(params)
        results.append(result)

    return results


def execute_by_env(params):
    environment = params.get('execution_env').get('env_name')
    
    if environment == LOCAL:
        result = executor_local.execute(params)
    
    elif environment == AWS_LAMBDA:
        result = executor_aws.execute(params)
    else:
        raise ValueError(f'Invalid execution environment: {environment}')
    
    return result
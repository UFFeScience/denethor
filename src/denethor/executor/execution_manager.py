from denethor.executor import executor_local, executor_aws
from denethor.environment import LOCAL, AWS_LAMBDA, AWS_EC2

FOR_EACH_INPUT = 'for_each_input'
FOR_ALL_INPUTS = 'for_all_inputs'

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
        - execution_env (dict): The execution environment.
        - configuration_id (dict): The configuration for the activity execution.
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
    
    if action != 'execute':
        raise ValueError(f"Invalid action={action} for Execution Manager of activity={activity_name}")
    
    if strategy != FOR_EACH_INPUT and strategy != FOR_ALL_INPUTS:
        raise ValueError(f"Invalid execution strategy={strategy} for Execution Manager of activity={activity_name}")
    
    print(f"\n>>>Execution Manager: {activity_name} | action={action} | strategy:={strategy} | all_input_data:={all_input_data}")

    results = []
    
    if strategy == FOR_EACH_INPUT:
        i = 0
        for input in all_input_data:
            i += 1
            params['iteration'] = i
            params['input_data'] = input
            params['all_input_data'] = all_input_data # TODO:Nem todas as funções requerem 'all_input_data'. Verificar a necessidade de passar esse parâmetro.
            result = execute_by_env(params)
            results.append(result)

    elif strategy == FOR_ALL_INPUTS:
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
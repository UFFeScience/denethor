import executor_local, executor_aws
from constants import LOCAL, AWS_LAMBDA, VM_LINUX


# params = {
#     'execution_id': execution_id,
#     'start_time_ms': start_time_ms,
#     'end_time_ms': end_time_ms,
#     'activity': activity,
#     'execution_env': execution_env,
#     'strategy': strategy,
#     'input_data': input_data
# }

def execute(params):
    activity_name = params.get('activity')
    strategy = params.get('strategy')
    all_input_data = params.get('input_data')
    
    print(f'Activity {activity_name} triggered with execution strategy: {strategy} for input data: {all_input_data}')

    results = []
    
    if strategy == 'for_each_input':
        for input in all_input_data:
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
import os
from utils import utils

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

def execute(params):
    
    activity_name = params.get('activity')
    execution_env = params.get('execution_env')

    payload = {
        'activity': activity_name, # nome da atividade
        'input_data': params.get('input_data'), # dados de entrada
        'all_input_data': params.get('all_input_data'), # conjunto completo dos dados de entrada
        'execution_env': execution_env # ambiente de execução
        }

    base_path = execution_env.get('base_path')
    activity_path = execution_env.get('activity_implementation_path')
    activity_path = os.path.join(base_path, activity_path)
    function_name = 'handler' # nome da função padrão dentro da implementação da atividade

    # Call the python function with the specified parameters and return the request ID
    result = utils.invoke_python(activity_name, activity_path, function_name, payload)
    
    return result
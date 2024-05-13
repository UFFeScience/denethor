from datetime import datetime
import json
import importlib
import os
import time
from utils import utils


print('******* Worflow execution started at: ', utils.now_str(), ' *******')
print('******* Working directory: ', os.getcwd(), ' *******')

# Set the workflow start time in milliseconds
start_time_ms = int(time.time() * 1000)
end_time_ms = None

# Load JSON files
with open('conf/workflow_config.json') as f: 
    workflow_config = json.load(f)

with open('conf/workflow_steps_local.json') as f: 
    workflow_steps = json.load(f)

# Load input files list to be used in the workflow
with open('conf/workflow_input_files.json', 'r') as f:
    input_files = json.load(f)

# Load the execution environment configuration
with open('conf/execution_env_config.json') as f:
    global_env_config = json.load(f)
    
#########################################################################
# FOR LOCAL TESTING!!!!
# Comment the following lines to run the workflow as usual
#########################################################################
    
# from datetime import datetime, timezone

# start_time_human = "2024-03-15 02:52:52Z"
# end_time_human   = "2024-03-15 02:53:26Z"

# # Converte a string para um objeto datetime
# start_time_date = datetime.strptime(start_time_human, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)
# end_time_date   = datetime.strptime(end_time_human, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)

# # Converte para milissegundos e acrescenta uma margem de 10 segundos
# # antes e depois do intervalo para garantir que todos os logs sejam capturados
# start_time_ms = int(start_time_date.timestamp() * 1000) - (10 * 1000)
# end_time_ms = int(end_time_date.timestamp() * 1000) + (10 * 1000)


# Steps id 5 and 6 are active

# for step in workflow_steps:
#     if step['id'] in (5,6):
#         step['active'] = True
#     else:
#         step['active'] = False

#########################################################################


# Workflow parameters
params = {
    'execution_id': utils.generate_execution_id(start_time_ms),
    'start_time_ms': start_time_ms,
    'end_time_ms': end_time_ms,
    'input_files': input_files,
    'step_params': None,
    'step_data': None
}

produced_data = {}

TREE_PATH = "data/executions/tree"
SUBTREE_PATH = "data/executions/subtree"
utils.remove_files(TREE_PATH) #TODO: provisório, remover após ajustar a execução local
utils.remove_files(SUBTREE_PATH) #TODO: provisório, remover após ajustar a execução local


# For each step in the workflow
for step in workflow_steps:
    # Check if the step is active
    if step.get('active', True):

        step_params = step.get('params')
        execution_env = step_params.get('execution_env')
        env_config = global_env_config.get(execution_env)
        
        # Load the execution environment configuration into the step parameters
        step_params['execution_env_config'] = env_config
        params['step_params'] =  step_params
        params['produced_data'] = produced_data
        
        # Call the python function with the specified parameters
        func_data = utils.invoke_python(step.get('module'),
                                        None,
                                        step.get('handler'),
                                        params)

        if func_data is not None:
            produced_data = {**produced_data, **func_data}

        print(f'\n>>> Function {step.get('handler')} from module {step.get('module')} called successfully')

    else:
        print(f'\n>>> Step id={step.get('step_id')}, handler={step.get('handler')} is inactive! Skipping...')

print('******* Workflow execution finished at: ', utils.now_str(), ' *******')
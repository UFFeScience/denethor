from datetime import datetime
import json
import importlib
import os
import time


print('******* Worflow execution started at: ', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ' *******')
print('******* Working directory: ', os.getcwd(), ' *******')

# Set the workflow start time
workflow_start_time_ms = int(time.time() * 1000)
workflow_start_time_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(workflow_start_time_ms/1000))



# Set the workflow execution ID
execution_id = 'EXEC_' + workflow_start_time_str.replace(':', '-').replace('T', '_').replace('Z', '') + '_UTC'

# Load JSON files
with open('conf/provider_conf.json') as f: 
    PROVIDER_CONF = json.load(f)

with open('conf/workflow_conf.json') as f: 
    WORKFLOW_CONF = json.load(f)

with open('conf/workflow_steps.json') as f: 
    WORKFLOW_STEPS = json.load(f)

# For testing purposes, you can override the start and end time of the logs to be retrieved
override_params = {
}

#########################################################################
#########################################################################
# FOR LOCAL TESTING!!!!
    
from datetime import datetime, timezone

start_time_human = "2024-03-15 02:52:52Z"
end_time_human   = "2024-03-15 02:53:26Z"

# Converte a string para um objeto datetime
start_time_date = datetime.strptime(start_time_human, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)
end_time_date   = datetime.strptime(end_time_human, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)

# Converte para milissegundos e acrescenta uma margem de 10 segundos
# antes e depois do intervalo para garantir que todos os logs sejam capturados
override_start_time_ms = int(start_time_date.timestamp() * 1000) - (10 * 1000)
override_end_time_ms = int(end_time_date.timestamp() * 1000) + (10 * 1000)
override_execution_id = 'EXEC_' + str(start_time_date).replace('T', '_').replace('+00:00', '_UTC').replace('-03:00', '_GMT3').replace(':', '-').replace(' ', '_').replace('Z', '')

override_params = {
    'override_start_time_ms': override_start_time_ms,
    'override_end_time_ms': override_end_time_ms,
    'override_execution_id': override_execution_id
}

# step_to_execute = "upload_files_to_aws_s3"
# step_to_execute = "invoke_lambda_execution"
# step_to_execute = "monitor_lambda_execution"
# step_to_execute = "invoke_lambda_execution"
# step_to_execute = "monitor_lambda_execution"
# step_to_execute = "download_files_from_aws_s3"
step_to_execute = "import_provenance_from_aws"

for step in WORKFLOW_STEPS['steps']:
    if step['handler'] == step_to_execute:
        step['active'] = True
    else:
        step['active'] = False

#########################################################################
#########################################################################








# Json file containing the list of input files
json_file = WORKFLOW_CONF['workflow']['input_files']['json_file']

# Load actual input files list to be used in the workflow
with open(json_file, 'r') as file:
    FILES = json.load(file)
    input_files_name = FILES['files']
    input_files_path = FILES['path']

# Limit the number of files to be used
file_limit = WORKFLOW_CONF['workflow']['input_files']['limit']
if file_limit is not None:
    input_files_name = input_files_name[:file_limit]

# Store workflow configuration and runtime parameters
workflow_params = {
    # Workflow and provider configuration parameters from the JSON file
    **PROVIDER_CONF, 
    **WORKFLOW_CONF, 
    # Workflow runtime parameters
    'execution_id': execution_id,
    'workflow_start_time_str': workflow_start_time_str,
    'workflow_start_time_ms': workflow_start_time_ms,
    'input_files_name': input_files_name,
    'input_files_path': input_files_path,
}

# Store the produced data of the activities at each step
steps_return_data = {
}

# For each step in the workflow
for step in WORKFLOW_STEPS['steps']:
    # Check if the step is active
    if step.get('active', True):
        # Import the module dynamically
        module = importlib.import_module(step['module'])

        # Get the python function from the module
        python_function = getattr(module, step['handler'])
        
        params = {
            **workflow_params,
            **steps_return_data,
            **step['params'],
            **override_params
        }
        print(f'\n>>> Calling python function {step['handler']} from module {step['module']} with params: {params}')
        # Call the python function with the specified parameters and store the produced data to be used in the next steps
        return_data = python_function(params)
        if return_data is not None:
            steps_return_data = {**steps_return_data, **return_data}

        print(f'\n>>> Function {step['handler']} from module {step['module']} called successfully')

    else:
        print(f'\n>>> Step {step['handler']} is inactive! Skipping...')

print('******* Workflow execution finished at: ', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ' *******')
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
    'input_files_path': input_files_path
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
            **step['params']
        }
        print(f'\n>>> Calling python function {step['handler']} from module {step['module']} with params: {params}')
        try:
            # Call the python function with the specified parameters and store the produced data to be used in the next steps
            return_data = python_function(params)
            if return_data is not None:
                steps_return_data = {**steps_return_data, **return_data}
        except Exception as e:
            print(f'\n>>> An error occurred: {str(e)}')
            raise(e)

        print(f'\n>>> Function {step['handler']} from module {step['module']} called successfully')

    else:
        print(f'\n>>> Step {step['handler']} is inactive! Skipping...')

print('******* Workflow execution finished at: ', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ' *******')
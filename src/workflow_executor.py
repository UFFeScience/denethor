import json
import importlib
import time

# Load JSON files
with open('config/providers.json') as f: 
    PROVIDERS_INFO = json.load(f)

with open('config/workflow.json') as f: 
    WORKFLOW_INFO = json.load(f)

with open('config/workflow_activities.json') as f: 
    ACTIVITIES_INFO = json.load(f)
    
# Set the workflow start time
workflow_start_time_ms = int(time.time() * 1000)
workflow_start_time_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(workflow_start_time_ms/1000))

# Set the workflow execution ID
execution_id = 'EXEC_' + workflow_start_time_str.replace(':', '-').replace('T', '_').replace('Z', '') + '_UTC'

# Load data files to be used in the workflow and limit the number of files to be used
with open(WORKFLOW_INFO['workflow']['dataFiles']['fileListJson'], 'r') as file:
    dataFiles = json.load(file)

limit = WORKFLOW_INFO['workflow']['dataFiles']['fileLimit']
if limit is not None:
    dataFiles = dataFiles[:limit]

# Set the workflow parameters
workflow_params = {
    "providers": PROVIDERS_INFO['providers'],
    "workflow": {"name": WORKFLOW_INFO['workflow']['workflow_name'], "description": WORKFLOW_INFO['workflow']['workflow_description']},
    "executionId": execution_id,
    "workflowStartTimeStr": workflow_start_time_str,
    "workflowStartTimeMs": workflow_start_time_ms,
    "dataFiles": dataFiles
}

# Store the execution parameters of the activities at each step
execution_params = {
}

# Para cada etapa no workflow
for step in WORKFLOW_INFO['workflow']['steps']:
    # Verificar se a etapa está ativa
    if step.get('active', True):
        # Importar o módulo que contém a função a ser chamada
        module = importlib.import_module(step['module'])
        # Obter a função a ser chamada
        function = getattr(module, step['handler'])
        
        params = workflow_params | execution_params | step['params']
        print(f'Calling function {step["handler"]} from module {step["module"]} with params: {params}')
        try:
            # Chamar a função com os parâmetros especificados
            return_data = function(params)
            execution_params[step['handler']] = return_data
        except Exception as e:
            print(f'An error occurred: {str(e)}')
            raise(e)

        print(f'Function {step["handler"]} from module {step["module"]} called successfully')

    else:
        print(f'Step {step["handler"]} is inactive! Skipping...')
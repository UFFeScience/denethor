import json
import importlib
import time

# Carregar o workflow do arquivo JSON
with open('config/workflow_model.json', 'r') as f:
    workflow_model = json.load(f)

    
workflow_start_time_ms = int(time.time() * 1000)
workflow_start_time_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(workflow_start_time_ms/1000))

execution_id = 'EXEC_' + workflow_start_time_str.replace(':', '-').replace('T', '_').replace('Z', '') + '_UTC'

workflow_params = {
    "serviceProvider": workflow_model['serviceProvider'],
    "workflow": {"name": workflow_model['workflow']['name'], "description": workflow_model['workflow']['description']},
    "executionId": execution_id,
    "workflowStartTimeStr": workflow_start_time_str,
    "workflowStartTimeMs": workflow_start_time_ms,
    "dataFiles": workflow_model['workflow']['dataFiles']
}

# Armarzenar os parâmetros de retorno das funções em tempo de execução
execution_params = {}

# Para cada etapa no workflow
for step in workflow_model['workflow']['steps']:
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
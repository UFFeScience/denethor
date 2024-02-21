import json
import importlib

# Carregar o workflow do arquivo JSON
with open('config/workflow_model.json', 'r') as f:
    workflow_model = json.load(f)

# Para cada etapa no workflow
for step in workflow_model['workflow']['steps']:
    # Verificar se a etapa está ativa
    if step.get('active', True):
        # Importar o módulo que contém a função a ser chamada
        module = importlib.import_module(step['module'])
        # Obter a função a ser chamada
        function = getattr(module, step['handler'])
        
        params = step['params'] | workflow_model['workflow']['dataFiles']
        print(f'Calling function {step["handler"]} from module {step["module"]} with params: {params}')
        try:
            # Chamar a função com os parâmetros especificados
            function(params)
        except Exception as e:
            print(f'An error occurred: {str(e)}')

        print(f'Function {step["handler"]} from module {step["module"]} called successfully')

    else:
        print(f'Step {step["handler"]} is inactive! Skipping...')
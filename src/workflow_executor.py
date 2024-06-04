import copy
import json
import os
import time
from utils import utils
from execution import execution_manager

local_win = 'local_win'
LAMBDA = 'LAMBDA'
VM_LINUX = 'VM_LINUX'

# Load JSON files
with open('conf/provider_info.json') as f: 
    provider = json.load(f)

with open('conf/workflow_info.json') as f: 
    workflow = json.load(f)

with open('conf/workflow_steps.json') as f: 
    workflow_steps = json.load(f)

with open('conf/statistics.json') as f: 
    statistics = json.load(f)

# Load the execution environment configuration
with open('conf/env_config.json') as f:
    global_env_config = json.load(f)

# Set the workflow start time in milliseconds
start_time_ms = int(time.time() * 1000)
end_time_ms = None
execution_id = utils.generate_execution_id(start_time_ms)



def main():

    print('******* Worflow execution started at: ', utils.now_str(), ' *******')
    print('******* Working directory: ', os.getcwd(), ' *******')

        
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


    TREE_PATH = "data/executions/tree"
    SUBTREE_PATH = "data/executions/subtree"
    utils.remove_files(TREE_PATH) #TODO: provisório, remover após ajustar a execução local
    utils.remove_files(SUBTREE_PATH) #TODO: provisório, remover após ajustar a execução local

    produced_data = {}

    # For each step in the workflow
    for step in workflow_steps:
        
        step_id = step.get('id')
        # Check if the step is active
        if step.get('active') is False:
            print(f'\n>>> Step [{step_id}], action: {step.get("action")}, activity: {step.get("activity")} is inactive. Skipping...')
            continue
            
        
        
        
        # se em step id anterior houver arquivos produzidos, usá-los como input_files

        # TODO: Verificar uma melhor forma de passar os arquivos da etpa anterior para a próxima etapa
        # tree_constructor
        
        # tree_files = []
        # for exec in steps_produced_data.get(1):
        #     tree_files.extend(exec.get('produced_files'))
        # if tree_files is not None and len(tree_files) > 0:
        #     # files = [f for lin in tree_files for f in lin]
        #     current_files = copy.deepcopy(tree_files)

        # # subtree_constructor
        # subtree_matrix = []
        # for exec in steps_produced_data.get(2):
        #     subtree_matrix.append(exec.get('produced_files'))
        # if subtree_matrix is not None and len(subtree_matrix) > 0:
        #     current_files = copy.deepcopy(subtree_matrix)

        # # subtree_maf: combine maf_database and max_maf
        # maf_database_list = {}
        # max_maf_list = {}
        # for exec in steps_produced_data.get(3):
        #     db = exec.get('maf_database')
        #     mm = exec.get('max_maf')
        #     if db is not None:
        #         maf_database_list.append(db)
        #     if mm is not None:
        #         max_maf_list.append(mm)                  
        
        # Load the execution environment configuration into the step parameters
        action = step.get('action')
        activity = step.get('activity')
        execution_env_name = step.get('execution_env')
        strategy = step.get('execution_strategy')
        execution_env = global_env_config.get(execution_env_name)
        execution_env = {'env_name': execution_env_name, **execution_env}

        input_data_param = step.get('data').get('input')
        limit = step.get('data').get('input_limit')
        output_param = step.get('data').get('output')
        if '.json' in input_data_param:
            # Load input files list to be used in the workflow
            with open(input_data_param, 'r') as f:
                input_data = json.load(f)
        
        else:
            # recuperar os dados da etapa anterior contidos no parametro indicado por 'input_data_param'
            for key, value in produced_data.items():
                if input_data_param == key:
                    input_data = [item['produced_data'] for item in value]
                    break

        if input_data is None:
            raise ValueError(f'Invalid input data: {input_data_param}')
        
        if limit is not None:
            input_data = input_data[:limit]  
                
        # Workflow parameters
        params = {
            'execution_id': execution_id,
            'start_time_ms': start_time_ms,
            'end_time_ms': end_time_ms,
            'activity': activity,
            'execution_env': execution_env,
            'strategy': strategy,
            'input_data': input_data,
            'output_param': output_param,
        }
        
        
        result = execution_manager.execute(params)
        
        produced_data[output_param] = result
                

        print(f'\n>>> Action {action} | activity {activity} completed.')

        

    print('******* Workflow execution finished at: ', utils.now_str(), ' *******')




if __name__ == '__main__':
    main()
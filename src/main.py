import os, time, json

# import sys
# sys.path.append("../denethor")

from denethor_utils import utils as du, file_utils as dfu
from denethor_executor import execution_manager as dem

conf_path = os.getcwd() + '/workflow_executor/conf/'
# Load JSON files
with open(conf_path + 'provider_info.json') as f:
    provider = json.load(f)

with open(conf_path + 'workflow_info.json') as f:
    workflow = json.load(f)

with open(conf_path + 'workflow_steps.json') as f:
    workflow_steps = json.load(f)

with open(conf_path + 'statistics.json') as f:
    statistics = json.load(f)

# Load the execution environment configuration
with open(conf_path + 'env_config.json') as f:
    global_env_config = json.load(f)

# Set the workflow start time in milliseconds
start_time_ms = int(time.time() * 1000)
end_time_ms = None
workflow_exec_id = du.generate_workflow_exec_id(start_time_ms)


def main():

    print('******* Worflow execution started at: ', du.now_str(), ' *******')
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


    tree_path = "data/executions/tree"
    subtree_path = "data/executions/subtree"
    dfu.remove_files(tree_path) #TODO: provisório, remover após ajustar a execução local
    dfu.remove_files(subtree_path) #TODO: provisório, remover após ajustar a execução local

    workflow_produced_data = {}

    # For each step in the workflow
    for step in workflow_steps:
        
        step_id = step.get('id')
        # Check if the step is active
        if step.get('active') is False:
            print(f'\n>>> Step [{step_id}], action: {step.get("action")}, activity: {step.get("activity")} is inactive. Skipping...')
            continue
            
        action = step.get('action')
        activity = step.get('activity')
        execution_env_name = step.get('execution_env')
        strategy = step.get('execution_strategy')
        execution_env = global_env_config.get(execution_env_name)

        input_param = step.get('params').get('input_param')
        limit_param = step.get('params').get('input_limit')
        output_param = step.get('params').get('output_param')
        
        if '.json' in input_param:
            # Load input files list to be used in the workflow
            with open(os.getcwd() + '/workflow_executor/' + input_param, 'r') as f:
                input_data = json.load(f)
        else:
            # recuperar os dados produzidos anteriormente indicados por 'input_param'
            # input_data será uma lista dos outputs produzidos pelas ativações
            for param, activity_output in workflow_produced_data.items():
                if input_param == param:
                    input_data = [output['produced_data'] for output in activity_output]
                    break

        if input_data is None:
            raise ValueError(f'Invalid input data: {input_param}')
        
        if limit_param is not None:
            input_data = input_data[:limit_param]  
                
        # Workflow parameters
        params = {
            'execution_id': workflow_exec_id,
            'start_time_ms': start_time_ms,
            'end_time_ms': end_time_ms,
            'activity': activity,
            'execution_env': execution_env,
            'strategy': strategy,
            'input_data': input_data
        }
        
        
        results = dem.execute(params)
        
        workflow_produced_data[output_param] = results
                

        print(f'\n>>> Action: {action} | activity: {activity} completed.')


    print('******* Workflow execution finished at: ', du.now_str(), ' *******')



if __name__ == '__main__':
    main()
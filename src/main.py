import os, time, json

# import sys
# sys.path.append("../src")

from denethor_utils import utils as du, file_utils as dfu
from denethor_executor import execution_manager as dem

conf_path = os.path.join(os.getcwd(), 'config')
# Load JSON files
with open(os.path.join(conf_path, 'provider_info.json'), 'r') as f:
    provider = json.load(f)

with open(os.path.join(conf_path, 'workflow_info.json'), 'r') as f:
    workflow = json.load(f)

with open(os.path.join(conf_path, 'workflow_steps.json'), 'r') as f:
    workflow_steps = json.load(f)

with open(os.path.join(conf_path, 'statistics.json'), 'r') as f:
    statistics = json.load(f)

# Load the execution environment configuration
with open(os.path.join(conf_path, 'env_config.json'), 'r') as f:
    env_configs = json.load(f)

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


    # tree_path = "data/executions/tree"
    # subtree_path = "data/executions/subtree"
    # dfu.remove_files(tree_path) #TODO: provisório, remover após ajustar a execução local
    # dfu.remove_files(subtree_path) #TODO: provisório, remover após ajustar a execução local

    workflow_produced_data = {}

    # For each step in the workflow
    for step in workflow_steps:
        
        step_id = step.get('id')
        action = step.get('action')
        activity = step.get('activity')
        
        # Check if the step is active
        if step.get('active') is False:
            print(f"\n>>> Step [{step_id}], action: {action}, activity: {activity} is inactive. Skipping...")
            continue
            
        env_name = step.get('execution_env')
        strategy = step.get('execution_strategy')
        # Get the execution environment configuration by the name set in the step
        execution_env = du.get_env_config_by_name(env_name, env_configs)

        input_param = step.get('params').get('input_param')
        output_param = step.get('params').get('output_param')
        
        # If the input parameter is a JSON file, load the data from the file
        if '.json' in input_param:
            # Load input files list to be used in the workflow
            with open(os.path.join(conf_path, input_param), 'r') as f:
                all_input_data = json.load(f)
        else:
            # recuperar os dados produzidos anteriormente indicados por 'input_param'
            # input_data será uma lista dos outputs produzidos pelas ativações
            for param_name, activity_output in workflow_produced_data.items():
                if input_param == param_name:
                    all_input_data = [output['produced_data'] for output in activity_output]
                    break

        if all_input_data is None:
            raise ValueError(f"Invalid input data: {input_param}")
        
        # Workflow parameters
        params = {
            'execution_id': workflow_exec_id,
            'start_time_ms': start_time_ms,
            'end_time_ms': end_time_ms,
            'activity': activity,
            'execution_env': execution_env,
            'strategy': strategy,
            'all_input_data': all_input_data
        }
        
        
        # Execute the activity
        results = dem.execute(params)
        
        # Save the produced data in the dictionary
        workflow_produced_data[output_param] = results
                

        print(f"\n>>> Action: {action} | activity: {activity} completed.")


    print('******* Workflow execution finished at: ', du.now_str(), ' *******')



if __name__ == '__main__':
    main()
import os, time, json
from pathlib import Path
from denethor_utils import env
from denethor_utils import utils as du, file_utils as dfu, env as denv
from denethor_executor import execution_manager as dem
import denethor_provenance.provenance.provenance_importer as dprov

# import sys
# sys.path.append("../src")
# from denethor_utils import log_handler as dlh

# FORCE_ENV = env.LOCAL
FORCE_ENV = ''

# Obter o caminho do arquivo atual
current_file = Path(__file__).resolve()

# Navegar até o diretório raiz do projeto
project_root = current_file.parent.parent

conf_path = os.path.join(project_root, 'config')
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

# Load input files list to be used in the workflow
with open(os.path.join(conf_path, 'input_files.json'), 'r') as f:
    input_files = json.load(f)

# Dictionary to store the produced data during the workflow execution
# Initial data is the "input_files" list
workflow_runtime_data = {
    "input_files": input_files
    }

def main():

    # Set the workflow start time in milliseconds
    start_time_ms = int(time.time() * 1000)
    end_time_ms = None


    ########################################################################
    # FOR LOCAL TESTING!!!!
    # Comment the following lines to run the workflow as usual
    ########################################################################
        
    from datetime import datetime, timezone

    # Define the start and end time parameters for log retrieval in aws cloudwatch
    
    BRAZIL_TZ = "-03:00"
    UTC_TZ = "-00:00"
    start_time_human = "2024-10-25T16:07:57" + UTC_TZ
    end_time_human   = "2024-10-25T16:08:35" + UTC_TZ

    # Convert the human-readable time to milliseconds
    start_time_ms = du.convert_str_to_ms(start_time_human)
    end_time_ms = du.convert_str_to_ms(end_time_human)

    # Adds a margin of 10 seconds before and after the interval to ensure that all logs are captured
    start_time_ms -= 10000
    end_time_ms += 10000

    # execution_id = du.generate_workflow_execution_id(start_time_ms)
    # execution_env = du.get_env_config_by_name("local", env_configs)
    # import denethor_utils.log_handler as dlh
    # logger = dlh.get_logger(execution_id, execution_env)
    # du.log_env_info(execution_env, logger)

    # Setting the active steps for testing
    # ["tree_constructor", "subtree_constructor", "maf_database_creator", "maf_database_aggregator"]
    action = "import_provenance"
    activities = ["tree_constructor", "subtree_constructor", "maf_database_creator", "maf_database_aggregator"]
    # activities = ["maf_database_aggregator"]

    for step in workflow_steps:
        if step['action'] == action and step['activity'] in activities:
            step['active'] = True
        else:
            step['active'] = False

    ########################################################################


    # tree_path = "data/executions/tree"
    # subtree_path = "data/executions/subtree"
    # dfu.remove_files(tree_path) #TODO: provisório, remover após ajustar a execução local
    # dfu.remove_files(subtree_path) #TODO: provisório, remover após ajustar a execução local



    # testing_execution = False
    # # testing_execution = True

    # if testing_execution:

    #     test_path = 'src/lambda_functions/tests/json'
        
    #     #open src/lambda_functions/tests/json/tree_constructor_10.json
    #     with open(os.path.join(test_path, 'subtree_constructor_10.json'), 'r') as f:
    #         tree_constructor_10 = json.load(f)
    #         data = [{
    #             "request_id" : "test_tree",
    #             "produced_data" : tree_constructor_10['all_input_data']
    #         }]
    #         workflow_produced_data['tree_files'] = data

    #     #open src/lambda_functions/tests/json/maf_db_creator_01st_x_05.json
    #     with open(os.path.join(test_path, 'maf_db_creator_01st_x_05.json'), 'r') as f:
    #         maf_db_creator_01st_x_05 = json.load(f)
    #         data = [{
    #             "request_id" : "test_subtree",
    #             "produced_data" : maf_db_creator_01st_x_05['all_input_data']
    #         }]
    #         workflow_produced_data['subtree_files'] = data

    
    execution_id = du.generate_workflow_execution_id(start_time_ms)
    
    print('>>>>>>> Main program started at: ', du.now_str())
    print('>>>>>>> Workflow start time is (ms):  ', start_time_ms)
    print('>>>>>>> Workflow start time is (str): ', du.convert_ms_to_str(start_time_ms))
    print('>>>>>>> Execution ID: ', execution_id)
    print('>>>>>>> Working directory: ', os.getcwd())
    
    # For each step in the workflow
    for step in workflow_steps:

        step_id = step.get('id')
        action = step.get('action')
        activity = step.get('activity')
        env_name = step.get('execution_env')
        if FORCE_ENV:
            env_name = FORCE_ENV
        # Get the execution environment configuration by the name set in the step
        execution_env = du.get_env_config_by_name(env_name, env_configs)
        
        # Check if the step is active
        if step.get('active') is False:
            print(f"\n>>> Step [{step_id}], action: {action}, activity: {activity} is inactive. Skipping...")
            continue

        if action != 'execute' and action != 'import_provenance':
            raise ValueError(f"Invalid action: {action} at step: {step_id} of activity: {activity}")
        
        if action == 'execute':
            
            strategy = step.get('strategy')

            if strategy != 'for_each_input' and strategy != 'for_all_inputs':
                raise ValueError(f"Invalid strategy: {strategy} at step: {step_id} of activity: {activity}")

            input_param = None
            output_param = None
            step_params = step.get('params')
            if step_params:
                input_param = step_params.get('input_param')
                output_param = step_params.get('output_param')
            
            # Validation of input parameter
            if step_params and input_param is None:
                raise ValueError(f"Invalid input parameter: {input_param} for step: {step_id}")
            
            # recuperar os dados runtime indicados por 'input_param'
            # input_data será uma lista dos outputs produzidos pelas ativações para uma atividade
            input_data = []
            if input_param == 'input_files':
                input_data = workflow_runtime_data['input_files']
            else:
                for param, data in workflow_runtime_data.items():
                    if param == input_param:
                        input_data = [item['data'] for item in data]
                        break
            
            # Validation of input data
            if input_data is None:
                raise ValueError(f"Invalid input data: {input_data} for step_params: {step_params} at step: {step_id}")
            
            # Workflow parameters
            step_params = {
                'execution_id': execution_id,
                'start_time_ms': start_time_ms,
                'end_time_ms': end_time_ms,
                'action': action,
                'activity': activity,
                'execution_env': execution_env,
                'strategy': strategy,
                'all_input_data': input_data
            }
            
            
            # Execute the activity
            results = dem.execute(step_params)
            
            # Save the produced data in the dictionary
            workflow_runtime_data[output_param] = results

        elif action == 'import_provenance':

            # Mesmo que o ambiente de execução seja local, é necessário obter as informações de log da AWS
            # com isso, tempo que pegar o env_config da AWS
            aws_env = du.get_env_config_by_name(denv.AWS_LAMBDA, env_configs)
            
            step_params = {
                'execution_id': execution_id,
                'start_time_ms': start_time_ms,
                'end_time_ms': end_time_ms,
                'activity': activity,
                'log_path': aws_env.get('log_config').get('path'),
                'log_file': aws_env.get('log_config').get('file_name'),
                'providers': provider,
                'workflow': workflow,
                'statistics': statistics
            }
            dprov.import_provenance_from_aws(step_params)
        

        print(f"\n>>> {activity} | action: {action} completed.")


    print('******* Workflow execution finished at: ', du.now_str(), ' *******')



if __name__ == '__main__':
    main()
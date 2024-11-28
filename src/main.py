import os, time, json
from pathlib import Path
from denethor import environment as denv
from denethor.utils import utils as du, file_utils as dfu
from denethor.executor import execution_manager as dem
import denethor.provenance.provenance_importer as dprov

# FORCE_ENV = env.LOCAL
FORCE_ENV = ''

# Raiz do projeto
project_root = Path(__file__).resolve().parent.parent

conf_path = os.path.join(project_root, 'conf')
# Load JSON files
with open(os.path.join(conf_path, 'provider.json'), 'r') as f:
    provider = json.load(f)

with open(os.path.join(conf_path, 'workflow.json'), 'r') as f:
    workflow = json.load(f)

with open(os.path.join(conf_path, 'workflow_execution.json'), 'r') as f:
    workflow_steps = json.load(f)

with open(os.path.join(conf_path, 'statistics.json'), 'r') as f:
    statistics = json.load(f)

# Load the environment configuration
env_properties = du.load_env_config(os.path.join(conf_path, 'env.properties'))

# Dictionary to store the produced data during the workflow execution
workflow_runtime_data = {}

def main():

    # Set the workflow start time in milliseconds
    start_time_ms = int(time.time() * 1000)
    end_time_ms = None


    ########################################################################
    # FOR LOCAL TESTING!!!!
    # Comment the following lines to run the workflow as usual
    ########################################################################
        
    # from datetime import datetime, timezone

    # # Define the start and end time parameters for log retrieval in aws cloudwatch
    
    # BRAZIL_TZ = "-03:00"
    # UTC_TZ = "-00:00"
    # start_time_human = "2024-10-25T16:07:57" + UTC_TZ #005 nova config
    # end_time_human   = "2024-10-25T16:08:35" + UTC_TZ

    # # Convert the human-readable time to milliseconds
    # start_time_ms = du.convert_str_to_ms(start_time_human)
    # end_time_ms = du.convert_str_to_ms(end_time_human)

    # # Adds a margin of 10 seconds before and after the interval to ensure that all logs are captured
    # start_time_ms -= 10000
    # end_time_ms += 10000

    # # execution_id = du.generate_workflow_execution_id(start_time_ms)
    # # execution_env = du.get_env_config_by_name("local", env_configs)
    # # import denethor.utils.log_handler as dlh
    # # logger = dlh.get_logger(execution_id, execution_env)
    # # du.log_env_info(execution_env, logger)

    # # Setting the active steps for testing
    # # ["tree_constructor", "subtree_constructor", "maf_database_creator", "maf_database_aggregator"]
    # action = "import_provenance"
    # activities = ["tree_constructor", "subtree_constructor", "maf_database_creator", "maf_database_aggregator"]
    # # activities = ["maf_database_aggregator"]

    # for step in workflow_steps:
    #     if step['action'] == action and step['activity'] in activities:
    #         step['active'] = True
    #     else:
    #         step['active'] = False

    ########################################################################


    execution_id = du.generate_workflow_execution_id(start_time_ms)
    
    print('>>>>>>> Main program started at: ', du.now_str())
    print('>>>>>>> Workflow start time is (ms):  ', start_time_ms)
    print('>>>>>>> Workflow start time is (str): ', du.convert_ms_to_str(start_time_ms))
    print('>>>>>>> Execution ID: ', execution_id)
    print('>>>>>>> Working directory: ', os.getcwd())
    
    # For each step in the workflow
    for step in workflow_steps:

        activity = step.get('activity')
        provider_code = step.get('provider')
        memory = step.get('memory')

        
        if FORCE_ENV:
            provider = FORCE_ENV
        
        
        # Check if the step is active
        if step.get('active') is False:
            print(f"\n>>> Step [{step_id}], action: {action}, activity: {activity} is inactive. Skipping...")
            continue

        strategy = step.get('strategy')

        if strategy != 'for_each_input' and strategy != 'for_all_inputs':
            raise ValueError(f"Invalid strategy: {strategy} at step: {step_id} of activity: {activity}")

        input_param_name = None
        output_param_name = None
        data_params = step.get('data_params')
        if data_params:
            input_dir = data_params.get('input_dir')
            input_param_name = data_params.get('input_param')
            output_param_name = data_params.get('output_param')
        
        # Validation of input parameter
        if data_params and input_param_name is None:
            raise ValueError(f"Invalid input parameter: {input_param_name} for activity: {activity}")
        
        
        # caso input_dir esteja presente, significa que os dados de entrada serão lidos de um diretório
        if input_dir and dfu.is_valid_path(input_dir):
            input_files = dfu.list_all_files(input_dir)
            workflow_runtime_data[input_param_name] = input_files

        
        # recuperar os dados  em runtime indicados por 'input_param_name'
        # input_data será uma lista dos dados necessários para a atividade corrente
        input_data = []
        for key, data in workflow_runtime_data.items():
            if key == input_param_name:
                input_data = [item['data'] for item in data]
                break
        
        # Validation of input data
        if input_data is None:
            raise ValueError(f"Invalid input data: {input_data} for step_params: {params} at step: {step_id}")
        
        # Workflow parameters
        params = {
            'execution_id': execution_id,
            'start_time_ms': start_time_ms,
            'end_time_ms': end_time_ms,
            'action': action,
            'activity': activity,
            'execution_env': env_params,
            'configuration_id': lambda_configuration_id,
            'strategy': strategy,
            'all_input_data': input_data
        }
        
        # Execute the activity
        results = dem.execute(params)
        
        # Save the produced data in the dictionary
        workflow_runtime_data[output_param_name] = results

        print(f"\n>>> {activity} | action: {action} completed.")



    #################################
    #  Import provenance data
    #################################
    
    # Mesmo que o ambiente de execução seja local, é necessário obter as informações de log da AWS
    # com isso, tempo que pegar o environment_params da AWS
    aws_env = du.get_env_params_by_name(denv.AWS_LAMBDA, env_params)
        
    # For each step in the workflow
    for step in workflow_steps:

        step_id = step.get('id')
        action = step.get('action')
        activity = step.get('activity')
        provider = step.get('execution_env')
        lambda_configuration_id = step.get('configuration')

        params = {
            'execution_id': execution_id,
            'start_time_ms': start_time_ms,
            'end_time_ms': end_time_ms,
            'activity': activity,
            'configuration_id': lambda_configuration_id,
            'log_path': aws_env.get('log_params').get('path'),
            'log_file': aws_env.get('log_params').get('file_name'),
            'providers': provider,
            'workflow': workflow,
            'statistics': statistics
        }

        dprov.import_provenance_from_aws(params)

    print('******* Workflow execution ', execution_id, ' finished at: ', du.now_str(), ' *******')
    # print('******* Executed activities: ', executed_activities, ' *******')
    # print('******* Provenance imported activities: ', provenance_imported_activities, ' *******')





if __name__ == '__main__':
    main()
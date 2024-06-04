from datetime import datetime
import json
import os
import platform

local_win = 'local_win'
LAMBDA = 'LAMBDA'
VM_LINUX = 'VM_LINUX'

# class Environment:
#     def __init__(self, execution_env):
#         # 'LAMBDA' or 'local_win' or 'VM_LINUX'
#         self.env = execution_env
#         self.TMP_PATH = None
#         self.DATASET_PATH = None
#         self.INPUT_PATH = None
#         self.OUTPUT_PATH = None
#         self.CLUSTALW_PATH = None
#         self.DATA_FORMAT = None
#         self.LIB_PATH = None
#         self.PLATFORM = platform.system()

#         if self.PLATFORM != 'Linux' and self.PLATFORM != 'Windows':
#             raise Exception('Unsupported OS')
        
#         # Load environment variables from config file
#         with open('lambda_functions/conf/env_config.json') as f:
#             env_config = json.load(f)

#         # Environment variables depending on the execution environment
#         self.DATA_FORMAT = env_config['DATA_FORMAT']

#         if self.env in env_config:
#             self.TMP_PATH = env_config[self.env]['TMP_PATH']
#             self.DATASET_PATH = env_config[self.env]['DATASET_PATH']
#             self.TREE_PATH = env_config[self.env]['TREE_PATH']
#             self.SUBTREE_PATH = env_config[self.env]['SUBTREE_PATH']
#             self.CLUSTALW_PATH = env_config[self.env]['CLUSTALW_PATH']
#         else:
#             raise Exception('Invalid execution environment: ' + self.env)


def print_path(label, path):
    if os.path.exists(path):
        print(f'{label}={path}:', os.listdir(path))
    else:
        print(f'{label} does not exist')

def print_env(env_name, env_conf):
    print(f'============== Ambiente de execução: {env_name} ==============')
    print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('pwd:', os.getcwd())
    for key, value in env_conf.items():
        print_path(label=key, path=value)
    
    print('===========================================================')

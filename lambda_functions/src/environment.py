from datetime import datetime
import json
import os
import platform

class Environment:
    def __init__(self, execution_env):
        # 'LAMBDA' or 'LOCAL_WIN' or 'VM_LINUX'
        self.env = execution_env
        self.TMP_PATH = None
        self.DATASET_PATH = None
        self.INPUT_PATH = None
        self.OUTPUT_PATH = None
        self.CLUSTALW_PATH = None
        self.DATA_FORMAT = None
        self.LIB_PATH = None
        self.PLATFORM = platform.system()

        if self.PLATFORM != 'Linux' and self.PLATFORM != 'Windows':
            raise Exception('Unsupported OS')
        
        # Load environment variables from config file
        with open('lambda_functions/conf/env_config.json') as f:
            env_config = json.load(f)

        # Environment variables depending on the execution environment
        self.DATA_FORMAT = env_config['DATA_FORMAT']

        if self.env in env_config:
            self.TMP_PATH = env_config[self.env]['TMP_PATH']
            self.DATASET_PATH = env_config[self.env]['DATASET_PATH']
            self.TREE_PATH = env_config[self.env]['TREE_PATH']
            self.SUBTREE_PATH = env_config[self.env]['SUBTREE_PATH']
            self.CLUSTALW_PATH = env_config[self.env]['CLUSTALW_PATH']
        else:
            raise Exception('Invalid execution environment: ' + self.env)



    def print_environment(self):
        print('============== Estado do ambiente de execução ==============')
        print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print('pwd:', os.getcwd())
        print('Environment:', self.env)
        
        if os.path.exists(self.TMP_PATH):
            print('TMP_PATH:', os.listdir(self.TMP_PATH))
        else:
            print('TMP_PATH does not exist')

        if os.path.exists(self.DATASET_PATH):
            print('DATASET_PATH:', os.listdir(self.DATASET_PATH))
        else:
            print('DATASET_PATH does not exist')

        if os.path.exists(self.TREE_PATH):
            print('TREE_PATH:', os.listdir(self.TREE_PATH))
        else:
            print('TREE_PATH does not exist')

        if os.path.exists(self.SUBTREE_PATH):
            print('SUBTREE_PATH:', os.listdir(self.SUBTREE_PATH))
        else:
            print('SUBTREE_PATH does not exist')

        if os.path.exists(self.CLUSTALW_PATH):
            print('CLUSTALW_PATH:', os.listdir(self.CLUSTALW_PATH))
        else:
            print('CLUSTALW_PATH does not exist')

        print('===========================================================')
    
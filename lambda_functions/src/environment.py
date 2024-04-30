import datetime
import json
import os
import platform

class Environment:
    def __init__(self, event):
        self.event = event
        self.TMP_PATH = None
        self.DATASET_PATH = None
        self.INPUT_PATH = None
        self.OUTPUT_PATH = None
        self.CLUSTALW_PATH = None
        self.DATA_FORMAT = None
        self.LIB_PATH = None
        self.PLATFORM = platform.system()

        if self.PLATFORM != 'Linux' or self.PLATFORM != 'Windows':
            raise Exception('Unsupported OS')
        
        # Load environment variables from config file
        with open('env_config.json') as f:
            env_config = json.load(f)

        # Environment variables depending on the execution environment
        env = event['execution_env']  # 'LAMBDA' or 'LOCAL_WIN' or 'VM_LINUX'
        self.DATA_FORMAT = env_config['DATA_FORMAT']

        if env in env_config:
            self.TMP_PATH = env_config[env]['TMP_PATH']
            self.DATASET_PATH = env_config[env]['DATASET_PATH']
            self.TREE_PATH = env_config[env]['TREE_PATH']
            self.SUBTREE_PATH = env_config[env]['SUBTREE_PATH']
            self.CLUSTALW_PATH = env_config[env]['CLUSTALW_PATH']
        else:
            raise Exception('Invalid execution environment: ' + env)



    def print_environment(self):
        print('============== Estado do ambiente de execução ==============')
        print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print('pwd:', os.getcwd())
        print('TMP_PATH:', os.listdir(self.TMP_PATH))
        print('DATASET_PATH:', os.listdir(self.DATASET_PATH))
        print('TREE_PATH:', os.listdir(self.TREE_PATH))
        print('SUBTREE_PATH:', os.listdir(self.SUBTREE_PATH))
        print('CLUSTALW_PATH:', os.listdir(self.CLUSTALW_PATH))
        print('DATA_FORMAT:', self.DATA_FORMAT)
        print('===========================================================')
    
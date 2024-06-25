from datetime import datetime, timezone
import os, re, json, uuid
from denethor.src.utils import denethor_logger as dl


def generate_uuid():
    return 'uuid_' + str(uuid.uuid4()).replace('-', '_')

def generate_workflow_exec_id(start_time_ms):
    return 'EXEC_' + to_str(start_time_ms).replace(':', '-').replace('T', '_').replace('Z', '') + '_UTC'

def get_request_id(context):
    return context.aws_request_id if context else generate_uuid()

def get_execution_env(event):
    return event.get('execution_env')

# Define a regex pattern to match only valid characters in file names or directories
def sanitize(filename):
    return re.sub(r'[^a-zA-Z0-9_\-\./]', '_', filename).replace("LATEST", '')



##
# Parse and Conversion functions
##

# Create datetime objects (in UTC) from the timestamps in milliseconds
def to_datetime(time: float):
    if time:
        return datetime.fromtimestamp((time / 1000.0), tz=timezone.utc)
    return None

def to_str(time: float):
    return to_datetime(time).strftime('%Y-%m-%dT%H:%M:%S')

def now_str():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

def to_str(json_obj: dict) -> str:
    return json.dumps(json_obj, indent=2)

def parse_int(value: str) -> int:
    if value is None:
        return None
    match = re.search(r"\d+", value)
    value_int = int(match.group()) if match else None
    return value_int

def parse_float(value: str) -> float:
    if value is None:
        return None
    match = re.search(r"\d+\.?\d*", value)
    value_float = float(match.group()) if match else None
    return value_float


def remove_files(dir_path):
    if os.path.exists(dir_path):
        # Walk through all files and directories within dir_path
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f'Removed the file {file_path}')
    else:
        print(f'Sorry, directory {dir_path} did not exist.')

def print_env(execution_env):
    print('===========================================================')
    print(f'=======================  {execution_env.get('env_name')}  =======================')
    print(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('pwd:', os.getcwd())
    for label, value in execution_env.items():
        print(f'{label}={value}')
        # print(os.listdir(value) if 'PATH' in label else '')  
    print('===========================================================')


def print_env_to_log(execution_env, logger):
    logger.info('===========================================================')
    logger.info(f'=======================  {execution_env.get('env_name')}  =======================')
    logger.info(f'Start time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info('pwd:', os.getcwd())
    for label, value in execution_env.items():
        logger.info(f'{label}={value}')
        # logger.info(os.listdir(value) if 'PATH' in label else '')  
    logger.info('===========================================================')


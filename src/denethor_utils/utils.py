from datetime import datetime, timezone
from logging import Logger
import os, re, json, uuid


def generate_uuid():
    return 'uuid_' + str(uuid.uuid4()).replace('-', '_')

def generate_workflow_exec_id(start_time_ms):
    return 'EXEC_' + to_str(start_time_ms).replace(':', '-').replace('T', '_').replace('Z', '') + '_UTC'

def get_request_id(context):
    return context.aws_request_id if context else generate_uuid()

def get_execution_env(event):
    return event.get('execution_env')

def get_env_config_by_name(env_name, global_env_config):
    pass#!!!!!!!! fazer a busca aqui

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
    if not value:
        return None
    match = re.search(r"\d+\.?\d*", value)
    value_float = float(match.group()) if match else None
    return value_float


def print_env_log(execution_env, logger: Logger):
    env_name = execution_env.get('env_name')
    logger.info('===========================================================')
    logger.info(f'=======================  {env_name}  =======================')
    logger.info(f'Start time: {now_str()}')
    logger.info(f'pwd={os.getcwd()}')
    for label, value in execution_env.items():
        logger.info(f'{label}={value}')
        logger.info(os.listdir(value) if 'PATH' in label else '')  
    logger.info('===========================================================')


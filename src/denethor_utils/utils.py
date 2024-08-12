from datetime import datetime, timezone
from logging import Logger
import os, re, json, uuid


def generate_uuid():
    return 'uuid_' + str(uuid.uuid4()).replace('-', '_')

def generate_workflow_execution_id(start_time_ms):
    return 'exec_' + convert_ms_to_str(start_time_ms).replace(':', '-').replace('T', '_').replace('Z', '').replace('+00-00', '_UTC')

def get_request_id(context):
    return context.aws_request_id if context else generate_uuid()

def get_execution_id(event):
    return event.get('execution_id')

def get_execution_env(event):
    return event.get('execution_env')

def get_env_config_by_name(env_name, configs):
    for config in configs:
        if config.get('env_name') == env_name:
            return config
    raise ValueError(f"Invalid environment name: {env_name}")

# Define a regex pattern to match only valid characters in file names or directories
def sanitize(file_name):
    return re.sub(r'[^a-zA-Z0-9_\-\./]', '_', file_name).replace("LATEST", '')



##
# Datetime conversion functions
##
def convert_ms_to_datetime(time: float) -> datetime:
    """
    Converts a timestamp in milliseconds to a datetime object (in UTC)
    """
    return datetime.fromtimestamp(time / 1000.0, tz=timezone.utc)


def convert_ms_to_str(time: float) -> str:
    """
    Converts a timestamp in milliseconds to a string in the format: 'YYYY-MM-DDTHH:MM:SS±HH:MM'
    """
    dt = datetime.fromtimestamp(time / 1000, tz=timezone.utc)
    return dt.isoformat()

def convert_str_to_ms(time: str) -> float:
    """
    Converts a string in the format: 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DDTHH:MM:SS±HH:MM' to a timestamp in milliseconds
    """
    dt = datetime.fromisoformat(time)
    return dt.timestamp() * 1000

def now_str() -> str:
    """
    Returns the current time in the format: 'YYYY-MM-DDTHH:MM:SS±HH:MM'
    """
    return datetime.now(timezone.utc).isoformat()

##
# Parse and Conversion functions
##
# def convert_json_to_str(json_obj: dict) -> str:
#     return json.dumps(json_obj, indent=2)

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


def flatten_list(input_list: list, level: int = None) -> list:
    """
    Flatten a list of lists into a single one up to a specified level
    """
    unique_elements = list()
    
    def flatten(item, current_level):
        if isinstance(item, list):
            if level is None or current_level < level:
                for subitem in item:
                    flatten(subitem, current_level + 1)
            else:
                unique_elements.append(item)
        else:
            unique_elements.append(item)
    
    flatten(input_list, 0)
    return list(unique_elements)


def log_env_info(env, logger: Logger):
    logger.info(f">>>> Environment={env.get('env_name')} | current_time={now_str()} | pwd={os.getcwd()}")
    for label, value in env.items():
        logger.info(f'>> {label}={value}')
        # logger.info(os.listdir(value) if 'PATH' in label else '')  
    


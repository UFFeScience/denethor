from datetime import datetime, timezone
from logging import Logger
import os, re, json, uuid
from typing import Dict
from configparser import ConfigParser



def generate_uuid():
    return 'uuid_' + str(uuid.uuid4()).replace('-', '_')

def generate_workflow_execution_id(start_time_ms):
    # return 'exec_' + convert_ms_to_str(start_time_ms).replace(':', '-').replace('T', '_').replace('Z', '').replace('+00-00', '_UTC')
    return 'weid_' + str(int(start_time_ms))


def resolve_request_id(context):
    return context.aws_request_id if context else generate_uuid()


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


# def flatten_list_level(input_list: list, level: int = None) -> list:
#     """
#     Flatten a list of lists into a single one up to a specified level
#     """
#     unique_elements = list()
    
#     def flatten(item, current_level):
#         if isinstance(item, list):
#             if level is None or current_level < level:
#                 for subitem in item:
#                     flatten(subitem, current_level + 1)
#             else:
#                 unique_elements.append(item)
#         else:
#             unique_elements.append(item)
    
#     flatten(input_list, 0)
#     return list(unique_elements)

def flatten_list(input_list: list) -> list:
    """
    Flatten a list of lists into a single one
    """
    if not isinstance(input_list, list):
        return [input_list]
    
    flattened_list = []
    for item in input_list:
        if isinstance(item, list):
            flattened_list.extend(flatten_list(item))
        else:
            flattened_list.append(item)
    
    return flattened_list


# Function to convert a section to a dictionary
def config_section_to_dict(config: ConfigParser, section: str) -> Dict[str, str]:
    if config.has_section(section):
        return {option: config.get(section, option) for option in config.options(section)}
    else:
        raise ValueError(f"Section {section} not found in the properties file. Existing sections: {config.sections()}")
    

# Load the properties from a file
def load_properties(file_path: str) -> ConfigParser:
    config = ConfigParser()
    config.read(file_path)
    return {section: config_section_to_dict(config, section) for section in config.sections()}

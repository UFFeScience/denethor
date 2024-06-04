from datetime import datetime, timezone
import importlib.util
import inspect
import json
import os
import sys
import re

# Define a regex pattern to match only valid characters in file names or directories
def sanitize(filename):
    return re.sub(r'[^a-zA-Z0-9_\-\./]', '_', filename).replace("LATEST", '')

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

def generate_execution_id(start_time_ms):
    return 'EXEC_' + to_str(start_time_ms).replace(':', '-').replace('T', '_').replace('Z', '') + '_UTC'

# def invoke_python(module_name, module_path, function_name, payload):
#     print(f'\n>>> Calling python function {function_name} from module {module_name} with params: {payload}')
#     if module_path is not None:
#         sys.path.append(module_path)
#     module = importlib.import_module(module_name)
#     python_function = getattr(module, function_name)
#     return python_function(payload)


def invoke_python(module_name, module_path, func_name, payload):
    # Check if the module and function exist
    if not module_name or not func_name:
        raise ValueError('Both module_name and function_name must be provided')

    if module_path is not None:
        sys.path.append(module_path)

    module = importlib.import_module(module_name)

    # Get the function from the module
    if hasattr(module, func_name):
        python_function = getattr(module, func_name)
    else:
        raise AttributeError(f'The module {module_name} does not have a function named {func_name}')

    # Check if the number of provided arguments matches the number of parameters the function requires
    params = inspect.signature(python_function).parameters
    num_none = len(params) - 1
    args = [payload] + ([None] * num_none)

    # Call the function with the provided arguments
    return python_function(*args)


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
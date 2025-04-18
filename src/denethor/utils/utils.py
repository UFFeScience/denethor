from datetime import datetime, timezone
from logging import Logger
import os, re, json, uuid
from typing import Dict
from configparser import ConfigParser


def generate_uuid():
    return "uuid_" + str(uuid.uuid4()).replace("-", "_")


def generate_execution_tag(start_time_ms):
    # return 'exec_' + convert_ms_to_str(start_time_ms).replace(':', '-').replace('T', '_').replace('Z', '').replace('+00-00', '_UTC')
    return "wetag_" + str(int(start_time_ms))


def resolve_request_id(context):
    return context.aws_request_id if context else generate_uuid()


# Define a regex pattern to match only valid characters in file names or directories
def sanitize(file_name):
    return re.sub(r"[^a-zA-Z0-9_\-\./]", "_", file_name).replace("LATEST", "")


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
        return {
            option: config.get(section, option) for option in config.options(section)
        }
    else:
        raise ValueError(
            f"Section {section} not found in the properties file. Existing sections: {config.sections()}"
        )


# Load the properties from a file
def load_properties(file_path: str) -> ConfigParser:
    config = ConfigParser()
    config.read(file_path)
    return {
        section: config_section_to_dict(config, section)
        for section in config.sections()
    }


# Function to override parameters in the workflow steps dictionary
def override_params(
    workflow_steps: dict,
    provider: str = None,
    memory: str = None,
    input_file_list: list = None,
    active_steps: list = None,
):
    for step in workflow_steps:
        if provider:
            step["provider"] = provider
            print(f"Warning: Overriding environment to {provider}!")
        if memory:
            step["memory"] = memory
            print(
                f"Warning: Overriding memory size of step {step['activity']} to {memory}MB!"
            )
        if input_file_list:
            if step.get("data_params") and step.get("data_params").get(
                "input_files_list"
            ):
                step["data_params"]["input_files_list"] = input_file_list
                print(
                    f"Warning: Overriding input files list of step {step['activity']} to {input_file_list}!"
                )
        if active_steps:
            if step["activity"] in active_steps:
                step["active"] = True
                print(f"Warning: Overriding step {step['activity']} to active!)")
            else:
                step["active"] = False
                print(f"Warning: Overriding step {step['activity']} to inactive!)")

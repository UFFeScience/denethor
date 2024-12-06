import os, sys
import importlib.util, inspect
from typing import Any, Dict


def invoke_local_python(
    module_identifier: str,
    module_path: str,
    target_method: str,
    payload: dict[str, str],
) -> Any:
    """
    Invokes a local Python function with the given module indentifer, path, method name, and payload.

    Args:
        module_identifier (str): The name of the module containing the target method.
        module_path (str): The path to the module if it is not in the default search path.
        target_method (str): The name of the method to be invoked.
        payload (Any): The payload to be passed as an argument to the method.

    Returns:
        Any: The result of the function call.

    Raises:
        ValueError: If both `module_identifier` and `target_method` are not provided.
        AttributeError: If the module does not have a method with the given name.
    """
    # Check if the module and function exist
    if not module_identifier or not module_path or not target_method:
        raise ValueError("Both module_name and function_name must be provided")

    sys.path.append(module_path)
    module = importlib.import_module(module_identifier)

    # Get the function from the module
    if hasattr(module, target_method):
        python_obj = getattr(module, target_method)
    else:
        raise AttributeError(
            f"The module {module_identifier} does not have a method named {target_method}"
        )

    # Check if the number of provided arguments matches the number of parameters the method requires
    params = inspect.signature(python_obj).parameters
    num_none = len(params) - 1
    args = [payload] + ([None] * num_none)

    # Call the method with the provided arguments
    return python_obj(*args)

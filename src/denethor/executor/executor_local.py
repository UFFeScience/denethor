import os, sys
import importlib.util, inspect


def invoke_python(module_name, module_path, func_name, payload):
    """
    Invokes a Python function with the given module name, function name, and payload.

    Args:
        module_name (str): The name of the module containing the target function.
        module_path (str): The path to the module if it is not in the default search path.
        func_name (str): The name of the function to be invoked.
        payload (Any): The payload to be passed as an argument to the function.

    Returns:
        Any: The result of the function call.

    Raises:
        ValueError: If both `module_name` and `func_name` are not provided.
        AttributeError: If the module does not have a function with the given name.
    """
    # Check if the module and function exist
    if not module_name or not module_path or not func_name:
        raise ValueError('Both module_name and function_name must be provided')

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

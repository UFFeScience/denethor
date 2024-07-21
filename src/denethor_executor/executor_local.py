import os, sys
import importlib.util, inspect


HANDLER = 'handler'

# params = {
#     'execution_id': execution_id,
#     'start_time_ms': start_time_ms,
#     'end_time_ms': end_time_ms,
#     'activity': activity,
#     'execution_env': execution_env,
#     'strategy': strategy,
#     'input_data': input_data,
#     'all_input_data': all_input_data,
#     'output_param': output_param,
# }

def execute(payload):
    
    activity_name = payload.get('activity')
    execution_env = payload.get('execution_env')

    base_path = execution_env.get('path_config').get('base')
    func_src_path = execution_env.get('path_config').get('functions_src')
    func_src_path = os.path.join(base_path, func_src_path)

    # Call the python function with the specified parameters and return the request ID
    result = invoke_python(activity_name, func_src_path, HANDLER, payload)
    
    return result


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

import os
import re

# Limpeza de arquivos #
def remove_files(dir_path: str) -> None:
    if os.path.exists(dir_path):
        # Walk through all files and directories within dir_path
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f'Removed the file {file_path}')
    else:
        print(f'Sorry, directory {dir_path} did not exist.')


def create_directory_if_not_exists(*dir_paths) -> None:
    for dir in dir_paths:
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True) # cria o diretório, caso não exista
            print(f'Directory {dir} was created!')


def directory_has_single_file(dir_path: str) -> bool:
    if not os.path.isdir(dir_path):
        return False
    files = os.listdir(dir_path)
    if len(files) != 1:
        return False
    return True

# Check if a path exists
def is_valid_path(path: str) -> bool:
    return os.path.exists(path)
    
# List all files in a directory
def list_all_files(dir_path: str) -> list:
    return list_files(dir_path, None)

def list_files(dir_path: str, filter: list[str]) -> list:

    # chek if dir_path is relative
    if not os.path.isabs(dir_path):
        dir_path = os.path.abspath(dir_path)

    # check if dir_path exists
    if not os.path.exists(dir_path):
        raise ValueError(f"Directory {dir_path} does not exist.")
    
    def natural_key(file):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', file)]

    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if not filter or file in filter:
                file_list.append(file)
    
    return sorted(file_list, key=natural_key)
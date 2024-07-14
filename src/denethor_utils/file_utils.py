import os

#
## LIMPEZA ##
#
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


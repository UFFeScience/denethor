import json

def choose_function():
    # Carregue as configurações do arquivo JSON
    with open('aws-log-manager/config.json', 'r') as f:
        configs = json.load(f)

    # Crie um menu com todos os nomes de funções
    print("Please choose a function:")
    for i, config in enumerate(configs, start=1):
        print(f"{i}. {config['function_name']}")

    # Peça ao usuário para escolher uma função
    choice = int(input("Enter the number of your choice: ")) 

    # Verifique se a escolha do usuário é válida
    if 1 <= choice <= len(configs):
        # Retorne a configuração escolhida como um dicionário
        return configs[choice - 1]
    else:
        print(f'Invalid choice: {choice}')
        return None
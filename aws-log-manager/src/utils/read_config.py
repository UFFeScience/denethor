import json

def choose_activity(config_data, pre_choice):
    # Obter a lista de funções
    functions = config_data['functions']

    # Perguntar ao usuário qual função ele deseja escolher
    print("Funções disponíveis:")
    for i, function in enumerate(functions, start=1):
        print(f"{i}. {function['functionName']}")

    if pre_choice:
        choice = pre_choice
    else:
        choice = int(input("Digite o número da função escolhida: "))

    # Verificar se a escolha é válida
    if 0 <= choice < len(functions):
        chosen_function = functions[choice -1]
        print(f"Você escolheu a função {chosen_function['functionName']}")
        return functions[choice -1]
    else:
        print("Escolha inválida")
        return None
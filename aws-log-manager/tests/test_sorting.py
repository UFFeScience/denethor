# # Cria uma lista de dicionários
# lista = [
#     {"logStreamName": "2024/01/16/[$LATEST]7zzzzzzzz", "timestamp": 1705442178632, "message": "Sorry, directory /tmp/trees did not exist.\n", "ingestionTime": 1705442184383, "eventId": "38032631476499179297730984551711416727584679242999070724"},
#     {"logStreamName": "2024/01/16/[$LATEST]7bbbbbbbb", "timestamp": 1705442178632, "message": "START RequestId: 0784fdf3-7ced-426f-9ba1-983591328ab7 Version: $LATEST\n", "ingestionTime": 1705442184383, "eventId": "38032631476499179297730984551711416727584679242999070721"},
#     {"logStreamName": "2024/01/16/[$LATEST]7bbbbbbbb", "timestamp": 1705442178640, "message": "START RequestId: 0784fdf3-7ced-426f-9ba1-983591328ab7 Version: $LATEST\n", "ingestionTime": 1705442184383, "eventId": "38032631476499179297730984551711416727584679242999070721"},
#     {"logStreamName": "2024/01/16/[$LATEST]7aaaaaaaa", "timestamp": 1705442177811, "message": "INIT_START Runtime Version: python:3.11.v25\tRuntime Version ARN: arn:aws:lambda:sa-east-1::runtime:a3304f2b48f740276b97ad9c52a9cc36a0bd9b44fecf74d0f1416aafb74e92fc\n", "ingestionTime": 1705442184383, "eventId": "38032631458190267489737342952510592025740374446589149184"},
#     {"logStreamName": "2024/01/16/[$LATEST]7aaaaaaaa", "timestamp": 1705442177000, "message": "INIT_START Runtime Version: python:3.11.v25\tRuntime Version ARN: arn:aws:lambda:sa-east-1::runtime:a3304f2b48f740276b97ad9c52a9cc36a0bd9b44fecf74d0f1416aafb74e92fc\n", "ingestionTime": 1705442184383, "eventId": "38032631458190267489737342952510592025740374446589149184"},
#     {"logStreamName": "2024/01/16/[$LATEST]7aaaaaaaa", "timestamp": 1705442177800, "message": "INIT_START Runtime Version: python:3.11.v25\tRuntime Version ARN: arn:aws:lambda:sa-east-1::runtime:a3304f2b48f740276b97ad9c52a9cc36a0bd9b44fecf74d0f1416aafb74e92fc\n", "ingestionTime": 1705442184383, "eventId": "38032631458190267489737342952510592025740374446589149184"},
#     {"logStreamName": "2024/01/16/[$LATEST]7aaaaaaaa", "timestamp": 1705442177813, "message": "INIT_START Runtime Version: python:3.11.v25\tRuntime Version ARN: arn:aws:lambda:sa-east-1::runtime:a3304f2b48f740276b97ad9c52a9cc36a0bd9b44fecf74d0f1416aafb74e92fc\n", "ingestionTime": 1705442184383, "eventId": "38032631458190267489737342952510592025740374446589149184"},
#     {"logStreamName": "2024/01/16/[$LATEST]7gggggggg", "timestamp": 1705442178632, "message": "Sorry, directory /tmp/input did not exist.\n", "ingestionTime": 1705442184383, "eventId": "38032631476499179297730984551711416727584679242999070722"},
#     {"logStreamName": "2024/01/16/[$LATEST]7eeeeeeee", "timestamp": 1705442178632, "message": "Directory /tmp/input was created!\n", "ingestionTime": 1705442184383, "eventId": "38032631476499179297730984551711416727584679242999070723"}
# ]

# # Ordena a lista pelo atributo logStreamName
# # lista_ordenada = sorted(lista, key=lambda x: x["logStreamName"])

# # Ordena a lista pelo atributo logStreamName e, em seguida, pelo atributo timestamp
# lista_ordenada = sorted(lista, key=lambda x: (x["logStreamName"], x["timestamp"]))

# # Exibe a lista ordenada
# # print(f"Lista ordenada: {lista_ordenada}")

# # Cria uma nova lista contendo apenas os valores desejados
# valores = [{x["logStreamName"], str(x["timestamp"])}  for x in lista]

# # Exibe a lista de valores
# print(f"Valores: {valores}")


import os

# O diretório onde os arquivos serão criados.
output_dir = "resources/data/test_download_files"

# Os tamanhos dos arquivos a serem criados, em bytes.
sizes = {
    "500KB": 500 * 1024,
    "1MB": 1 * 1024 * 1024,
    "5MB": 5 * 1024 * 1024,
    "10MB": 10 * 1024 * 1024,
    "50MB": 50 * 1024 * 1024,
}

# Um exemplo de texto "lorem ipsum".
lorem_ipsum_text = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

# Cria o diretório de saída se ele não existir.
os.makedirs(output_dir, exist_ok=True)

# Limpa arquivos antigos
for filename in os.listdir(output_dir):
    file_path = os.path.join(output_dir, filename)
    if os.path.isfile(file_path):
        os.unlink(file_path)


# Gera os arquivos.
for size_name, size_in_bytes in sizes.items():
    file_path = os.path.join(output_dir, f"{size_name}.txt")
    print(f"Gerando {file_path} com tamanho {size_name}...")
    with open(file_path, "w") as f:
        bytes_written = 0
        while bytes_written < size_in_bytes:
            f.write(lorem_ipsum_text)
            bytes_written = f.tell()
    # Trunca o arquivo para o tamanho exato
    with open(file_path, 'rb+') as f:
        f.seek(size_in_bytes)
        f.truncate()

print("Arquivos gerados com sucesso.")

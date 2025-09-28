import os
from workflow_generator_random import WorkflowGeneratorRandom

# --- PARÂMETROS DE ENTRADA ---

OUTPUT_DIR = "resources/data/instance_files/synthetic/synthetic_random"

# Seção de resumo
NUM_TASKS = 6
NUM_DATA_ARTIFACTS = 8
NUM_VMS = 2
NUM_CONFIGS = 2
NUM_BUCKET_RANGES = 3

# Atributo para escolher o tipo de tempo
USE_INTEGER_TIME = True

# --- FIM DOS PARÂMETROS ---

def main():
    print("Iniciando a geração do arquivo de workflow sintético...")

    generator = WorkflowGeneratorRandom(
        num_tasks=NUM_TASKS,
        num_data=NUM_DATA_ARTIFACTS,
        num_vms=NUM_VMS,
        num_configs=NUM_CONFIGS, # Passando o novo parâmetro
        num_bucket_ranges=NUM_BUCKET_RANGES,
        use_integer_time=USE_INTEGER_TIME
    )

    # Gera o conteúdo do arquivo
    workflow_content = generator.generate_workflow_file_content()

    # Salva o conteúdo em um arquivo
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_base = f"synthetic_random_T{NUM_TASKS}_D{NUM_DATA_ARTIFACTS}_C{NUM_CONFIGS}"
    file_ext = ".txt"

    seq = 1
    output_path = os.path.join(OUTPUT_DIR, f"{file_base}_{seq:03d}{file_ext}")
    while os.path.exists(output_path):
        seq += 1
        output_path = os.path.join(OUTPUT_DIR, f"{file_base}_{seq:03d}{file_ext}")

    with open(output_path, 'w') as f:
        f.write(workflow_content)

    print("-" * 50)
    print(f"Arquivo '{output_path}' gerado com sucesso!")
    print(f"Resumo da Geração:")
    print(f"  - Tarefas: {NUM_TASKS}")
    print(f"  - Configs por Tarefa: {NUM_CONFIGS}")
    print(f"  - Dados: {generator.params['data']} (ajustado se necessário)")
    print(f"  - VMs: {NUM_VMS}")
    print(f"  - Tempos como {'Inteiros' if USE_INTEGER_TIME else 'Fracionários'}")
    print("-" * 50)

if __name__ == "__main__":
    main()
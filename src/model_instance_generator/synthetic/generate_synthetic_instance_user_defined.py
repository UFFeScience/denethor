import os
from workflow_generator_user_defined import WorkflowGeneratorUserDefined, parse_user_defined_workflows

# --- PARÂMETROS DE ENTRADA ---

INPUT_FILE = "resources/data/instance_files/synthetic/synthetic_user_defined/synthetic_workflows_definition.txt"
OUTPUT_DIR = "resources/data/instance_files/synthetic/synthetic_user_defined"

# Seção de resumo
NUM_VMS = 2
NUM_CONFIGS = 2
NUM_BUCKET_RANGES = 3

# Atributo para escolher o tipo de tempo
USE_INTEGER_TIME = True

# --- FIM DOS PARÂMETROS ---

def main():
    print("Iniciando a geração do arquivo de workflow sintético...")

    workflows = parse_user_defined_workflows(INPUT_FILE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for idx, wf in enumerate(workflows, 1):
        generator = WorkflowGeneratorUserDefined(
            workflow_id=wf['workflow_id'],
            num_tasks=wf['num_tasks'],
            num_data=wf['num_data'],
            task_defs=wf['task_defs'],
            output_dir=OUTPUT_DIR,
            num_vms=NUM_VMS,
            num_configs=NUM_CONFIGS,
            num_bucket_ranges=NUM_BUCKET_RANGES,
            use_integer_time=USE_INTEGER_TIME
        )
        file_base = f"{wf['workflow_id']}_T{wf['num_tasks']}_D{wf['num_data']}_C{NUM_CONFIGS}"
        file_ext = ".txt"
        file_name = f"{file_base}{file_ext}"
        output_path = os.path.join(OUTPUT_DIR, file_name)
        with open(output_path, 'w') as f:
            f.write(generator.generate_workflow_file_content())
        print(f"Arquivo '{output_path}' gerado com sucesso!")
        
    print("Total de arquivos gerados:", len(workflows))

if __name__ == "__main__":
    main()
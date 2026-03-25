import os
from workflow_generator_user_defined import WorkflowGeneratorUserDefined, parse_user_defined_workflows

# --- PARÂMETROS DE ENTRADA ---

INPUT_FILE = "resources/data/instance_files/synthetic/synthetic_user_defined/my_synthetic_instances_definition.txt"
OUTPUT_DIR = "resources/data/instance_files/synthetic/synthetic_user_defined"

# IDs de workflow a pular (não regenerar)
SKIP_WORKFLOW_IDS = {"Synthetic_7"}

# Seção de resumo
NUM_VMS = 2
NUM_CONFIGS = 2
NUM_BUCKET_RANGES = 3

# Atributo para escolher o tipo de tempo
USE_INTEGER_TIME = True

# Parâmetros para substituir prefixos de IDs
# Deixe None para não fazer substituição
TASK_PREFIX_REPLACE = {'old': 't', 'new': '1'} # para trocar t1, t2, etc por 11, 12, etc
DATA_PREFIX_REPLACE = {'old': 'd', 'new': '9'} # para trocar d1, d2, etc por 91, 92, etc

# --- FIM DOS PARÂMETROS ---

def main():
    print("Iniciando a geração do arquivo de workflow sintético...")

    workflows = parse_user_defined_workflows(INPUT_FILE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generated = 0
    for idx, wf in enumerate(workflows, 1):
        if wf['workflow_id'] in SKIP_WORKFLOW_IDS:
            print(f"Pulando workflow '{wf['workflow_id']}' (na lista SKIP_WORKFLOW_IDS).")
            continue
        generator = WorkflowGeneratorUserDefined(
            workflow_id=wf['workflow_id'],
            num_tasks=wf['num_tasks'],
            num_data=wf['num_data'],
            task_defs=wf['task_defs'],
            output_dir=OUTPUT_DIR,
            num_vms=NUM_VMS,
            num_configs=NUM_CONFIGS,
            num_bucket_ranges=NUM_BUCKET_RANGES,
            use_integer_time=USE_INTEGER_TIME,
            task_prefix_replace=TASK_PREFIX_REPLACE,
            data_prefix_replace=DATA_PREFIX_REPLACE
        )
        file_base = f"{wf['workflow_id']}_T{wf['num_tasks']}_D{wf['num_data']}_C{NUM_CONFIGS}"
        file_ext = ".txt"
        file_name = f"{file_base}{file_ext}"
        output_path = os.path.join(OUTPUT_DIR, file_name)
        with open(output_path, 'w') as f:
            f.write(generator.generate_workflow_file_content())
        print(f"Arquivo '{output_path}' gerado com sucesso!")
        generated += 1
        
    print("Total de arquivos gerados:", generated)

if __name__ == "__main__":
    main()
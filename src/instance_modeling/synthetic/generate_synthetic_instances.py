import os
import sys
import argparse
import re

from model.workflow_gen_random import WorkflowGeneratorRandom
from model.workflow_gen_user import WorkflowGeneratorUserDefined, parse_user_defined_workflows

# ==========================================
# --- CONFIGURAÇÃO PADRÃO DE EXECUÇÃO ---
# ==========================================
# Podem ser sobrescritas via linha de comando

# Modo de geração da instância sintética
GENERATION_MODE = "user" # random or user

# Para o caso de geração de instância em modo definido pelo usuário, 
# escolhe quais workflows serão considerados para geração
USER_TARGET_WORKFLOW_IDS = ["Synthetic_007"]  # Ex: ["Synthetic_007", "Synthetic_011"]. Se vazio, não gera nenhum.

# ==========================================
# --- PARÂMETROS COMPARTILHADOS ---
# ==========================================
NUM_VMS = 2
NUM_CONFIGS = 2
NUM_BUCKET_RANGES = 3
USE_INTEGER_TIME = True

# ==========================================
# --- PARÂMETROS PARA MODO 'RANDOM' ---
# ==========================================
RANDOM_OUTPUT_DIR = "resources/data/instance_files/synthetic/synthetic_random"
RANDOM_NUM_TASKS = 6
RANDOM_NUM_DATA_ARTIFACTS = 8

# ==========================================
# --- PARÂMETROS PARA MODO 'USER' ---
# ==========================================
USER_INPUT_FILE = "resources/data/instance_files/synthetic/synthetic_user_defined/my_synthetic_instances_definition.txt"
USER_OUTPUT_DIR = "resources/data/instance_files/synthetic/synthetic_user_defined"
TASK_PREFIX_REPLACE = {'old': 't', 'new': '1'}
DATA_PREFIX_REPLACE = {'old': 'd', 'new': '9'}


def build_filename(base_id, num_tasks, num_configs, num_data, num_vms):
    """Cria o nome do arquivo no padrão: Synthetic_<ID>_T<tasks>_C<configs>_D<data>_VM<vms>.txt"""
    match = re.search(r'\d+', str(base_id))
    num_id = int(match.group(0)) if match else 0
    return f"Synthetic_{num_id:03d}_T{num_tasks}_C{num_configs}_D{num_data}_VM{num_vms}.txt"


def save_and_print_instance(output_dir, file_name, content, num_tasks, num_configs, num_data, num_vms, mode_name):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, file_name)
    
    with open(output_path, 'w') as f:
        f.write(content)
        
    print(f"Arquivo '{output_path}' gerado com sucesso!")
    print(f"Resumo da Geração [{mode_name}]:")
    print(f"  - Tarefas: {num_tasks}")
    print(f"  - Configs por Tarefa: {num_configs}")
    print(f"  - Dados: {num_data}")
    print(f"  - VMs: {num_vms}")
    print("-" * 50)


def generate_random_content():
    """Apenas gera e retorna o conteúdo e os metadados do modo random."""
    generator = WorkflowGeneratorRandom(
        num_tasks=RANDOM_NUM_TASKS,
        num_data=RANDOM_NUM_DATA_ARTIFACTS,
        num_vms=NUM_VMS,
        num_configs=NUM_CONFIGS,
        num_bucket_ranges=NUM_BUCKET_RANGES,
        use_integer_time=USE_INTEGER_TIME
    )
    
    workflow_content = generator.generate_workflow_file_content()
    return workflow_content, generator.num_tasks, generator.num_configs, generator.num_data, generator.num_vms


def generate_user_contents(target_ids=None):
    """Apenas gera e retorna uma lista com os conteúdos e metadados do modo user."""
    if not os.path.exists(USER_INPUT_FILE):
        print(f"Erro: Arquivo de entrada '{USER_INPUT_FILE}' não encontrado. Verifique seu diretório de execução.")
        sys.exit(1)
        
    workflows = parse_user_defined_workflows(USER_INPUT_FILE)
    results = []
    
    for wf in workflows:
        if wf['workflow_id'] not in target_ids:
            # Ignora se o ID não está na lista a ser gerada
            continue
            
        generator = WorkflowGeneratorUserDefined(
            workflow_id=wf['workflow_id'],
            num_tasks=wf['num_tasks'],
            num_data=wf['num_data'],
            task_defs=wf['task_defs'],
            output_dir=USER_OUTPUT_DIR,
            num_vms=NUM_VMS,
            num_configs=NUM_CONFIGS,
            num_bucket_ranges=NUM_BUCKET_RANGES,
            use_integer_time=USE_INTEGER_TIME,
            task_prefix_replace=TASK_PREFIX_REPLACE,
            data_prefix_replace=DATA_PREFIX_REPLACE
        )
        
        content = generator.generate_workflow_file_content()
        results.append((wf['workflow_id'], content, generator.num_tasks, generator.num_configs, generator.num_data, generator.num_vms))
        
    return results


def process_random():
    print(f"\n[MODO RANDOM] Iniciando a geração de workflow sintético aleatório...")
    content, tasks, configs, data, vms = generate_random_content()
    
    seq = 1
    while True:
        file_name = build_filename(seq, tasks, configs, data, vms)
        if not os.path.exists(os.path.join(RANDOM_OUTPUT_DIR, file_name)):
            break
        seq += 1
        
    save_and_print_instance(RANDOM_OUTPUT_DIR, file_name, content, tasks, configs, data, vms, "Random")


def process_user(target_ids=None):
    print(f"\n[MODO USER] Iniciando a geração a partir do arquivo definido pelo usuário...")
    results = generate_user_contents(target_ids)
    
    generated = 0
    for wf_id, content, tasks, configs, data, vms in results:
        file_name = build_filename(wf_id, tasks, configs, data, vms)
        save_and_print_instance(USER_OUTPUT_DIR, file_name, content, tasks, configs, data, vms, f"User | ID: {wf_id}")
        generated += 1
        
    print(f"Total de arquivos gerados (User): {generated}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador de Instâncias Sintéticas do Denethor.")
    parser.add_argument('--mode', choices=['random', 'user'], default=GENERATION_MODE,
                        help=f"Escolha o modo de geração: 'random' ou 'user' (padrão: {GENERATION_MODE}).")
    parser.add_argument('--workflows', nargs='*', default=USER_TARGET_WORKFLOW_IDS,
                        help="Lista de IDs específicos para gerar no modo 'user' (ex: Synthetic_011 Synthetic_012). Se omitido, gera todos.")
    args = parser.parse_args()
    
    if args.mode == 'random': process_random()
    elif args.mode == 'user': process_user(args.workflows)
    
    print("\nGeração concluída.")
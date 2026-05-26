#!/usr/bin/env python3
"""
Script para recalcular limites seguros de TM e CM nas instâncias originais.

Ele faz a leitura estruturada dos arquivos, simula o cenário mais pessimista possível 
(TM avaliando máquinas mais lentas e I/O sequencial em VM vs paralelo em FX)
e reescreve a linha de cabeçalho do arquivo diretamente, mantendo a formatação original.
"""

import argparse
import sys
from pathlib import Path

# ==========================================
# BLOCO 1: Parsing e Leitura
# ==========================================

def _parse_int_list(s: str) -> list:
    s = s.strip().strip('[]')
    if not s:
        return []
    return [int(x.strip()) for x in s.split(',')]

def _parse_value(s: str) -> float:
    s = s.strip()
    return -1.0 if s == 'None' else float(s)

def parse_instance_data(lines: list):
    data_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
    if not data_lines:
        return None
        
    idx = 0
    p = data_lines[idx].split()
    idx += 1
    
    nTasks, nConfigs, nData, nVMs = int(p[0]), int(p[1]), int(p[2]), int(p[3])
    
    tasks = []
    for _ in range(nTasks):
        p = data_lines[idx].split()
        idx += 1
        tasks.append({
            'id': int(p[0]),
            'vmCpuTime': float(p[3]),
            'inputs': _parse_int_list(p[5]),
            'outputs': _parse_int_list(p[7])
        })
        
    data_map = {}
    for _ in range(nData):
        p = data_lines[idx].split()
        idx += 1
        data_map[int(p[0])] = {
            'readTime': _parse_value(p[2]),
            'writeTime': _parse_value(p[3])
        }
        
    vms = []
    for _ in range(nVMs):
        p = data_lines[idx].split()
        idx += 1
        vms.append({
            'id': int(p[0]),
            'slowdown': float(p[1]),
            'costPerSecond': float(p[2])
        })
        
    fx_configs = {}
    for _ in range(nTasks * nConfigs):
        p = data_lines[idx].split()
        idx += 1
        fx_configs.setdefault(int(p[0]), []).append({
            'cost': float(p[3]),
            'timeInit': float(p[5]),
            'timeCpu': float(p[6])
        })
        
    return tasks, data_map, vms, fx_configs

# ==========================================
# BLOCO 2: Regras Matemáticas e Upper Bounds
# ==========================================

def calculate_tm_cm(tasks, data_map, vms, fx_configs, filename=""):
    print(f"--- Calculando limites para {filename} ---")
    total_tm = 0.0
    base_cost_sum = 0.0
    
    for task in tasks:
        max_duration = 0.0
        max_cost = 0.0
        
        # --- Avaliação do pior cenário em VMs (I/O Sequencial) ---
        io_read_vm = sum(max(1.0, data_map[d]['readTime']) for d in task['inputs'])
        io_write_vm = sum(max(1.0, data_map[d]['writeTime']) for d in task['outputs'])
        
        for vm in vms:
            cpu_vm = max(1.0, task['vmCpuTime'] * vm['slowdown'])
            duration_vm = max(1.0, cpu_vm + io_read_vm + io_write_vm)
            cost_vm = duration_vm * vm['costPerSecond']
            
            max_duration = max(max_duration, duration_vm)
            max_cost = max(max_cost, cost_vm)
                
        # --- Avaliação do pior cenário em FX (I/O Paralelo) ---
        io_read_fx = max((max(1.0, data_map[d]['readTime']) for d in task['inputs']), default=0.0)
        io_write_fx = max((max(1.0, data_map[d]['writeTime']) for d in task['outputs']), default=0.0)
        
        print(f"  Task {task['id']}:")
        print(f"    VM I/O -> Read: {io_read_vm:.4f}, Write: {io_write_vm:.4f} (Sequencial)")
        print(f"    FX I/O -> Read: {io_read_fx:.4f}, Write: {io_write_fx:.4f} (Paralelo)")
        
        for fx in fx_configs.get(task['id'], []):
            duration_fx = max(1.0, fx['timeInit'] + fx['timeCpu'] + io_read_fx + io_write_fx)
            cost_fx = fx['cost']
            
            max_duration = max(max_duration, duration_fx)
            max_cost = max(max_cost, cost_fx)
                
        print(f"    Max Duration: {max_duration:.4f}, Max Base Cost: {max_cost:.10f}")
        
        total_tm += max_duration
        base_cost_sum += max_cost
        
    # A penalidade máxima possível (VM ligada ociosa de 0 a TM)
    max_idle_penalty = sum(vm['costPerSecond'] * total_tm for vm in vms)
    total_cm = base_cost_sum + max_idle_penalty
    
    print(f"  -> Total Base Cost: {base_cost_sum:.10f}")
    print(f"  -> Max Idle Penalty: {max_idle_penalty:.10f}")
    print(f"  -> Final TM: {total_tm:.4f}")
    print(f"  -> Final CM: {total_cm:.10f}\n")
    
    return total_tm, total_cm

# ==========================================
# BLOCO 3: Processamento de Arquivos In-Place
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="Atualiza TM e CM nas instâncias .txt")
    parser.add_argument("--instances-dir", type=Path, default=Path(""),
                        help="Caminho relativo ou absoluto para o diretório de instâncias")
    parser.add_argument("--patterns", nargs="+", default=["*.txt"],
                        help="Lista de padrões para filtrar arquivos (ex: Synthetic_007*.txt). Use * como curinga.")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    target_dir = (script_dir / args.instances_dir).resolve()

    if not target_dir.exists():
        print(f"Erro: Diretório {target_dir} não encontrado.")
        sys.exit(1)

    matched_files = set()
    for pattern in args.patterns:
        matched_files.update(target_dir.glob(pattern))
    
    matched_files = sorted(list(matched_files))

    if not matched_files:
        print(f"Nenhum arquivo encontrado em {target_dir} com os padrões: {args.patterns}")
        return

    print(f"Encontrados {len(matched_files)} arquivos para processar.\n")

    for filepath in matched_files:
        print(f"Lendo arquivo: {filepath.name}")
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        parsed = parse_instance_data(lines)
        if not parsed:
            print(f"Aviso: Arquivo {filepath.name} não possui dados válidos.\n")
            continue
            
        tasks, data_map, vms, fx_configs = parsed
        new_tm, new_cm = calculate_tm_cm(tasks, data_map, vms, fx_configs, filepath.name)
        
        # Substitui in-place a primeira linha válida de dados (onde estão CM e TM)
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                parts = line.strip().split()
                if len(parts) >= 8:
                    old_tm, old_cm = parts[6], parts[7]
                    parts[6] = f"{new_tm:.4f}"
                    parts[7] = f"{new_cm:.10f}"
                    lines[i] = "\t".join(parts) + "\n"
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                        
                    print(f"[{filepath.name}] Arquivo atualizado e salvo:")
                    print(f"  TM: {old_tm} -> {new_tm:.4f}")
                    print(f"  CM: {old_cm} -> {new_cm:.10f}\n")
                    print("="*60 + "\n")
                break

if __name__ == "__main__":
    main()
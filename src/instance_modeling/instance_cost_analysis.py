"""
Objetivo deste script (ler_instancia):
- Ler arquivos de instancia (.txt) no formato Denethor.
- Fazer analise exploratoria de custo para comparar:
  1) melhor custo por configuracao FX (seção de configs),
  2) melhor custo por VM (usando cpu_slowdown e cost_per_second).

Observacao:
- Este script NAO e o validador oficial.
- A validacao estrutural/semantica fica em:
    src/instance_modeling/validate_instance_file.py
"""

from typing import Dict, List, Tuple

try:
    from instance_modeling.instance_io import (
        ConfigRow,
        DataRow,
        TaskRow,
        VmRow,
        load_workflow_instance,
    )
except ImportError:
    from instance_io import (  # type: ignore
        ConfigRow,
        DataRow,
        TaskRow,
        VmRow,
        load_workflow_instance,
    )


def calculate_best_fx_cost(tasks: List[TaskRow], configs: List[ConfigRow]) -> Tuple[float, Dict[str, ConfigRow]]:
    """Retorna o menor custo total somando a melhor config de cada tarefa."""
    total_cost = 0.0
    best_configs: Dict[str, ConfigRow] = {}

    for task in tasks:
        task_configs = [c for c in configs if c.task_id == task.task_id and c.activity_id == task.activity_id]
        if not task_configs:
            continue

        min_config = min(task_configs, key=lambda c: c.task_cost)
        best_configs[task.task_id] = min_config
        total_cost += min_config.task_cost

    return total_cost, best_configs


def _data_by_id(datas: List[DataRow], data_id: str) -> DataRow | None:
    for data_row in datas:
        if data_row.data_id == data_id:
            return data_row
    return None


def _read_time(datas: List[DataRow], data_id: str) -> float:
    row = _data_by_id(datas, data_id)
    if row is None or row.read_time_avg is None:
        return 0.0
    return float(row.read_time_avg)


def _write_time(datas: List[DataRow], data_id: str) -> float:
    row = _data_by_id(datas, data_id)
    if row is None or row.write_time_avg is None:
        return 0.0
    return float(row.write_time_avg)


def calculate_best_vm_cost(tasks: List[TaskRow], datas: List[DataRow], vms: List[VmRow]) -> Tuple[float, Dict[str, Tuple[str, float, VmRow]]]:
    """Retorna o menor custo total somando a melhor VM por tarefa."""
    total_cost = 0.0
    best_vms: Dict[str, Tuple[str, float, VmRow]] = {}

    for task in tasks:
        vm_costs: List[Tuple[str, float, VmRow]] = []

        for vm in vms:
            read_duration = sum(_read_time(datas, did) for did in task.input_ids)
            write_duration = sum(_write_time(datas, did) for did in task.output_ids)
            total_duration = task.vm_cpu_time + read_duration + write_duration
            cost = total_duration * vm.cpu_slowdown * vm.cost_per_second
            vm_costs.append((vm.vm_id, cost, vm))

        if not vm_costs:
            continue

        vm_id, min_cost, vm_obj = min(vm_costs, key=lambda x: x[1])
        best_vms[task.task_id] = (vm_id, min_cost, vm_obj)
        total_cost += min_cost

    return total_cost, best_vms


def main() -> None:
    base_path = "resources/data/instance_files/synthetic/synthetic_user_defined"
    file_names = [
        "Synthetic_7_T3_D4_C2.txt",
        "Synthetic_11_T4_D7_C2.txt",
        "Synthetic_12_T5_D7_C2.txt",
        "Synthetic_13_T5_D8_C2.txt",
        "Synthetic_22_T8_D14_C2.txt",
    ]

    for file_name in file_names:
        print("\n\n*****************************************************************")
        print(f"Processando arquivo: {file_name}")

        header, tasks, datas, vms, configs, _bucket_ranges = load_workflow_instance(f"{base_path}/{file_name}")
        print(header)

        fx_total_cost, best_fx_configs = calculate_best_fx_cost(tasks, configs)
        print(f"\nMelhor custo de FX: {fx_total_cost:.10f}")
        for task_id, conf in best_fx_configs.items():
            print(f"Tarefa {task_id}: conf_id={conf.conf_id}, custo={conf.task_cost:.10f}")

        vm_total_cost, best_vm_choices = calculate_best_vm_cost(tasks, datas, vms)
        print(f"\nMelhor custo de VMs: {vm_total_cost:.10f}")
        for task_id, (vm_id, vm_cost, _vm_obj) in best_vm_choices.items():
            print(f"Tarefa {task_id}: VM={vm_id}, custo={vm_cost:.10f}")


if __name__ == "__main__":
    main()

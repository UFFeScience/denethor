import random, textwrap
import re

class WorkflowGeneratorModel:
    DEFAULT_VMS = [
        "1\t1.00000\t0.0000051670\t8589934592\t1250",
        "2\t0.50000\t0.0000206670\t8589934592\t1250",
        "3\t0.25000\t0.0000826720\t8589934592\t5000",
        "4\t0.12500\t0.0001653330\t8589934592\t5000",
        "5\t0.03125\t0.0006800000\t8589934592\t12500"
    ]
    DEFAULT_BUCKETS = [
        "1\t0\t54975581388800\t0.0000000000377185642719268799",
        "2\t54975581388800\t494780232499200\t0.0000000000363215804100036621",
        "3\t494780232499200\t107374182399998926258176\t0.0000000000344589352607727051"
    ]

    def __init__(self, num_tasks, num_data, num_vms, num_configs=1, num_bucket_ranges=3,
                 max_running_time=100.0, max_financial_cost=0.1, use_integer_time=False):
        
        # Validação dos parâmetros extras
        if num_vms > len(self.DEFAULT_VMS):
            raise ValueError(f"O número de VMs ({num_vms}) não pode ser maior que o número de VMs pré-definidas ({len(self.DEFAULT_VMS)}).")
        
        if num_bucket_ranges > len(self.DEFAULT_BUCKETS):
            raise ValueError(f"O número de faixas de bucket ({num_bucket_ranges}) não pode ser maior que o número de faixas pré-definidas ({len(self.DEFAULT_BUCKETS)}).")
        
        self.num_tasks = num_tasks
        self.num_configs = num_configs
        self.num_data = num_data
        self.num_vms = num_vms
        self.num_bucket_ranges = num_bucket_ranges
        self.max_running_time = max_running_time
        self.max_financial_cost = max_financial_cost
        self.use_integer_time = use_integer_time
        self.tasks = []
        self.data_artifacts = {}
        self._model_built = False
        self._static_data_ids = set()
        self._dynamic_data_ids = set()

    def _get_time(self, min_val, max_val):
        if self.use_integer_time:
            return random.randint(min_val, max_val)
        return random.uniform(min_val, max_val)

    def _format_time(self, value, precision=4):
        if value is None:
            return "None"
        if self.use_integer_time:
            return f"{int(round(value)):.{precision}f}"
        return f"{value:.{precision}f}"

    def _extract_num(self, id_str):
        match = re.search(r"(\d+)$", id_str)
        if match:
            return (id_str[:match.start()], int(match.group(1)))
        return (id_str, 0)

    def _sort_ids(self, ids):
        return sorted(ids, key=self._extract_num)

    def _ensure_model_generated(self):
        if self._model_built:
            return
        self.tasks, self.data_artifacts = self._build_tasks_and_data_model()
        self._validate_num_data()
        self._classify_data_artifacts()
        self._validate_data_artifacts_invariants()
        self._model_built = True

    def _validate_num_data(self):
        actual_count = len(self.data_artifacts)
        if self.num_data != actual_count:
            raise ValueError(
                f"num_data inconsistente: esperado {self.num_data}, encontrado {actual_count} artefatos de dados."
            )

    def _classify_data_artifacts(self):
        output_ids = {did for task in self.tasks for did in task["outputs"]}
        all_data_ids = set(self.data_artifacts.keys())
        self._dynamic_data_ids = output_ids & all_data_ids
        self._static_data_ids = all_data_ids - output_ids

        for did in all_data_ids:
            data_info = self.data_artifacts[did]
            data_info.setdefault("read_time", 0)
            data_info.setdefault("write_time", 0)
            data_info.setdefault("size_bytes", 0)

            if data_info.get("write_time") in (0, 0.0):
                data_info["write_time"] = None

            if did in self._static_data_ids:
                data_info["is_static"] = 1
                data_info["n_source_devices"] = 1
                data_info["write_time"] = None
            else:
                data_info["is_static"] = 0
                data_info["n_source_devices"] = 0

    def _validate_data_artifacts_invariants(self):
        """Fail fast if generated data metadata violates static/dynamic rules."""
        for did, data_info in self.data_artifacts.items():
            is_static = data_info.get("is_static")
            write_time = data_info.get("write_time")
            n_source_devices = data_info.get("n_source_devices")

            if did in self._static_data_ids:
                if is_static != 1:
                    raise ValueError(f"Data artifact {did} deveria ser is_static=1")
                if write_time is not None:
                    raise ValueError(f"Data artifact {did} estatico deveria ter write_time=None")
                if n_source_devices is None or n_source_devices < 1:
                    raise ValueError(f"Data artifact {did} estatico deveria ter n_source_devices>=1")
            else:
                if is_static != 0:
                    raise ValueError(f"Data artifact {did} dinamico deveria ser is_static=0")
                if write_time is None or write_time <= 0:
                    raise ValueError(f"Data artifact {did} dinamico deveria ter write_time>0")
                if n_source_devices != 0:
                    raise ValueError(f"Data artifact {did} dinamico deveria ter n_source_devices=0")

    # Seção 1: Cabeçalho do arquivo (resumo de parâmetros)
    def format_summary_section(self):
        # Seção 1: Cabeçalho do arquivo (resumo de parâmetros)
        header = "#<#tasks> <#config> <#data> <#vms> <#buckets> <#bucket_ranges> <max_running_time> <max_financial_cost>"
        line = f"{self.num_tasks}\t{self.num_configs}\t{self.num_data}\t{self.num_vms}\t1\t{self.num_bucket_ranges}\t{self.max_running_time}\t{self.max_financial_cost}"
        return f"{header}\n{line}\n"

    # Seção 2: Tarefas
    def format_tasks_section(self):
        self._ensure_model_generated()

        tasks_header = "#<task_id> <activity_id> <task_type__0-VM__1-VM_FX> <vm_cpu_time> <n_input> [<id_input>...] <n_output> [<id_output>...]"
        return f"{tasks_header}\n" + "\n".join(self._render_tasks_lines()) + "\n"

    # Seção 3: Dados
    def format_data_section(self):
        self._ensure_model_generated()

        data_header = "#<data_id> <data_size_bytes> <read_time_avg> <write_time_avg> <is_static> <n_source_devices> [<device_id>...]"
        return f"{data_header}\n" + "\n".join(self._render_data_lines()) + "\n"

    def _render_tasks_lines(self):
        lines = []
        for task in sorted(self.tasks, key=lambda t: self._extract_num(t["id"])):
            inputs = self._sort_ids(task["inputs"])
            outputs = self._sort_ids(task["outputs"])
            cpu_time = self._format_time(task["cpu_time"])
            lines.append(
                f"{task['id']}\t{task['activity_id']}\t1\t{cpu_time}\t{len(inputs)}\t[{','.join(inputs)}]\t{len(outputs)}\t[{','.join(outputs)}]"
            )
        return lines

    def _render_data_lines(self):
        lines = []
        for data_id in self._sort_ids(self.data_artifacts.keys()):
            data_info = self.data_artifacts[data_id]
            size_bytes = data_info.get("size_bytes", 0)
            read_time = self._format_time(data_info.get("read_time"))
            write_time = self._format_time(data_info.get("write_time"))
            is_static = data_info.get("is_static", 0)
            n_source_devices = data_info.get("n_source_devices", 0)
            lines.append(
                f"{data_id}\t{size_bytes:>5}\t{read_time}\t{write_time}\t{is_static}\t{n_source_devices}\t[denethor_bucket]"
            )
        return lines

    # Seção 4: VMs
    def format_vms_section(self):
        header = "#<vm_id> <cpu_slowdown> <cost_per_second> <storage_bytes> <bandwidth_mbps>"
        # Garante que o VM com id 1 sempre esteja presente
        vm1 = self.DEFAULT_VMS[0]
        remaining_vms = self.DEFAULT_VMS[1:]
        if self.num_vms == 1:
            lines = [vm1]
        else:
            lines = [vm1] + random.sample(remaining_vms, self.num_vms - 1)
        return f"{header}\n" + "\n".join(lines) + "\n"

    # Seção 5: Resultados de execução por tarefa/configuração
    def format_execution_results_section(self):
        
        self._ensure_model_generated()
        header = "#<task_id> <activity_id> <conf_id> <task_cost> <task_time_duration> <task_time_init> <task_time_cpu> <task_time_read> <task_time_write> <task_count>"
        lines = []
        num_configs = self.num_configs
        base_cost_per_second = 0.000005 # Custo de referência por segundo
        
        


        for task in self.tasks:
            # Tempos de I/O são os mesmos para todas as configs da mesma tarefa
            task_time_read = sum(self.data_artifacts[did]['read_time'] for did in task['inputs'])
            task_time_write = sum((self.data_artifacts[did]['write_time'] or 0) for did in task['outputs'])
            base_cpu_time = task['cpu_time']
            
            # A Fx da config 1 deve ser de 2x a 50x mais lenta que a VM base
            fx_base_time = base_cpu_time * random.uniform(2.0, 50.0)

            for conf_id in range(1, num_configs + 1):
                scaled_cpu_time = fx_base_time
                cost_multiplier = 1.0

                # Aplica fator de aceleração e de custo para configs > 1
                if conf_id > 1:

                    # CPU fica mais rápida conforme conf_id aumenta
                    speedup_factor = 1.0 + (conf_id - 1) * random.uniform(0.4, 0.8)
                    scaled_cpu_time = fx_base_time / speedup_factor

                    # Custo por segundo aumenta conforme conf_id aumenta
                    cost_multiplier = 1.0 + (conf_id - 1) * random.uniform(0.9, 1.5)

                # Se estiver usando tempos inteiros, arredondar para manter a consistência
                if self.use_integer_time:
                    scaled_cpu_time = round(scaled_cpu_time)

                # Calcula o custo e duração total para esta configuração específica
                task_cost = scaled_cpu_time * (base_cost_per_second * cost_multiplier)
                task_time_duration = task_time_read + task_time_write + scaled_cpu_time

                task_time_init = 0.0
                task_count = random.randint(1, 10)

                lines.append(
                    f"{task['id']}\t{task['activity_id']}\t{conf_id}\t{task_cost:.10f}\t{task_time_duration:.4f}\t{task_time_init:.4f}\t{scaled_cpu_time:.4f}\t{task_time_read:.4f}\t{task_time_write:.4f}\t{task_count}"
                )

        return f"{header}\n" + "\n".join(lines) + "\n"


    # Seção 6: Buckets de armazenamento
    def format_buckets_section(self):

        header = "#<bucket_range_id> <size1_bytes> <size2_bytes> <cost_per_byte>"
        lines = self.DEFAULT_BUCKETS[:self.num_bucket_ranges]
        return f"{header}\n" + "\n".join(lines) + "\n"


    # Seção 7: Estrutura do DAG (opcional)
    def format_dag_section(self):
        self._ensure_model_generated()

        static_data_str = ",".join(f"{i}" for i in self._sort_ids(self._static_data_ids))
        dynamic_data_str = ",".join(f"{i}" for i in self._sort_ids(self._dynamic_data_ids))

        task_lines = []
        for task in sorted(self.tasks, key=lambda t: self._extract_num(t["id"])):
            inputs_str = ",".join(f"{i}" for i in self._sort_ids(task["inputs"])) if task["inputs"] else "None"
            outputs_str = ",".join(f"{i}" for i in self._sort_ids(task["outputs"])) if task["outputs"] else "None"
            task_lines.append(f"{task['id']}: {inputs_str} -> {outputs_str}")

        # Monta a seção completa
        header_lines = [
            f"TASKS: {self.num_tasks}",
            f"DATA: {self.num_data}",
            f"STATIC_DATA: {static_data_str}",
            f"DYNAMIC_DATA: {dynamic_data_str}",
            "---"
        ]
        
        section_content = "\n".join(header_lines + task_lines)
        return section_content + "\n"

    # Gera as seções em ordem
    def generate_workflow_file_content(self):
        """ Monta e retorna o conteúdo completo do arquivo de workflow. """
        summary_section = self.format_summary_section()
        tasks_section = self.format_tasks_section()
        data_section = self.format_data_section()
        vms_section = self.format_vms_section()
        results_section = self.format_execution_results_section()
        buckets_section = self.format_buckets_section()
        # dag_section = self.format_dag_section()
        dag_section = ""
        
        # Concatena todas as seções
        full_content = (
            summary_section + "\n" +
            tasks_section + "\n" +
            data_section + "\n" +
            vms_section + "\n" +
            results_section + "\n" +
            buckets_section + "\n" +
            dag_section
        )
        return textwrap.dedent(full_content)

    def _build_tasks_and_data_model(self):
        """Implemented by subclasses: return (tasks, data_artifacts)."""
        raise NotImplementedError("Subclasses must implement _build_tasks_and_data_model().")

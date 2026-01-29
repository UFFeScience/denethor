import random, textwrap
import re

class WorkflowGenerator:
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

    def _get_time(self, min_val, max_val):
        if self.use_integer_time:
            return random.randint(min_val, max_val)
        return random.uniform(min_val, max_val)

    def generate_summary_section(self):
        header = "#<#tasks> <#config> <#data> <#vms> <#buckets> <#bucket_ranges> <max_running_time> <max_financial_cost>"
        line = f"{self.num_tasks}\t{self.num_configs}\t{self.num_data}\t{self.num_vms}\t1\t{self.num_bucket_ranges}\t{self.max_running_time}\t{self.max_financial_cost}"
        return f"{header}\n{line}\n"

    def generate_tasks_and_data_sections(self):
        """ Gera as seções de definição de tarefas e de dados. """
        tasks_lines, data_lines = self._generate_dag_and_data()
        
        tasks_header = "#<task_id> <activity_id> <task_type__0-VM__1-VM_FX> <vm_cpu_time> <n_input> [<id_input>...] <n_output> [<id_output>...]"
        data_header = "#<data_id> <data_size_bytes> <read_time_avg> <write_time_avg> <is_static> <n_source_devices> [<device_id>...]"
        
        tasks_section = f"{tasks_header}\n" + "\n".join(tasks_lines) + "\n"
        data_section = f"{data_header}\n" + "\n".join(data_lines) + "\n"
        
        return tasks_section, data_section

    def generate_vms_section(self):
        """ Gera a seção de VMs, usando os dados pré-definidos. """
        header = "#<vm_id> <cpu_slowdown> <cost_per_second> <storage_bytes> <bandwidth_mbps>"
        # Garante que o VM com id 1 sempre esteja presente
        vm1 = self.DEFAULT_VMS[0]
        remaining_vms = self.DEFAULT_VMS[1:]
        if self.num_vms == 1:
            lines = [vm1]
        else:
            lines = [vm1] + random.sample(remaining_vms, self.num_vms - 1)
        return f"{header}\n" + "\n".join(lines) + "\n"

    def generate_execution_results_section(self):
        """
        Gera a seção de resultados, criando uma entrada para cada tarefa
        em cada configuração (config_id).
        """
        header = "#<task_id> <activity_id> <conf_id> <task_cost> <task_time_duration> <task_time_init> <task_time_cpu> <task_time_read> <task_time_write> <task_count>"
        lines = []
        num_configs = self.num_configs
        base_cost_per_second = 0.000005 # Custo de referência por segundo

        for task in self.tasks:
            # Tempos de I/O são os mesmos para todas as configs da mesma tarefa
            task_time_read = sum(self.data_artifacts[did]['read_time'] for did in task['inputs'])
            task_time_write = sum(self.data_artifacts[did]['write_time'] for did in task['outputs'])
            base_cpu_time = task['cpu_time']

            for conf_id in range(1, num_configs + 1):
                scaled_cpu_time = base_cpu_time
                cost_multiplier = 1.0

                # Aplica fator de aceleração e de custo para configs > 1
                if conf_id > 1:

                    # CPU fica mais rápida conforme conf_id aumenta
                    speedup_factor = 1.0 + (conf_id - 1) * random.uniform(0.4, 0.8)
                    scaled_cpu_time = base_cpu_time / speedup_factor

                    # Custo por segundo aumenta conforme conf_id aumenta
                    cost_multiplier = 1.0 + (conf_id - 1) * random.uniform(0.9, 1.5)

                # Calcula o custo e duração total para esta configuração específica
                task_cost = scaled_cpu_time * (base_cost_per_second * cost_multiplier)
                task_time_duration = task_time_read + task_time_write + scaled_cpu_time

                task_time_init = 0.0
                task_count = random.randint(1, 10)

                lines.append(
                    f"{task['id']}\t{task['activity_id']}\t{conf_id}\t{task_cost:.10f}\t{task_time_duration:.4f}\t{task_time_init:.4f}\t{scaled_cpu_time:.4f}\t{task_time_read:.4f}\t{task_time_write:.4f}\t{task_count}"
                )

        return f"{header}\n" + "\n".join(lines) + "\n"

    def generate_buckets_section(self):
        """ Gera a seção de buckets de armazenamento. """

        header = "#<bucket_range_id> <size1_bytes> <size2_bytes> <cost_per_byte>"
        lines = self.DEFAULT_BUCKETS[:self.num_bucket_ranges]
        return f"{header}\n" + "\n".join(lines) + "\n"

    def generate_dag_section(self):
        """ Gera a seção com a estrutura do DAG. """
        
        # Determina todos os dados presentes no workflow como união de inputs e outputs de cada tarefa
        all_data_ids = set()
        dynamic_data_ids = set()
        for task in self.tasks:
            all_data_ids.update(task['inputs'])
            all_data_ids.update(task['outputs'])
            dynamic_data_ids.update(task['outputs'])

        # Dados estáticos são todos os outros
        static_data_ids = all_data_ids - dynamic_data_ids

        # Função para extrair o número do final do id
        def extract_num(id_str):
            match = re.search(r'(\d+)$', id_str)
            return int(match.group(1)) if match else 0

        # Formata as strings de dados
        static_data_str = ",".join(
            f"{i}" for i in sorted(static_data_ids, key=extract_num)
        )
        dynamic_data_str = ",".join(
            f"{i}" for i in sorted(dynamic_data_ids, key=extract_num)
        )

        # Monta as linhas de definição das tarefas
        task_lines = []
        # Ordena as tarefas pelo número no final do id
        for task in sorted(self.tasks, key=lambda t: extract_num(t['id'])):
            inputs_str = ",".join(f"{i}" for i in sorted(task['inputs'], key=extract_num)) if task['inputs'] else "None"
            outputs_str = ",".join(f"{i}" for i in sorted(task['outputs'], key=extract_num)) if task['outputs'] else "None"
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

    def generate_workflow_file_content(self):
        """ Monta e retorna o conteúdo completo do arquivo de workflow. """
        
        # Gera as seções em ordem
        summary_section = self.generate_summary_section()
        tasks_section, data_section = self.generate_tasks_and_data_sections()
        vms_section = self.generate_vms_section()
        results_section = self.generate_execution_results_section()
        buckets_section = self.generate_buckets_section()
        # dag_section = self.generate_dag_section()
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

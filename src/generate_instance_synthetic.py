import random
import textwrap

class WorkflowGenerator:
    """
    Gera instâncias de workflow artificiais baseadas em parâmetros definidos.
    """
    # Dados padrão baseados no arquivo de exemplo para VMs e Buckets
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

    def __init__(self, num_tasks, num_data, num_vms, num_configs=1, num_buckets=1, num_bucket_ranges=3,
                 max_running_time=100.0, max_financial_cost=0.1, use_integer_time=False):
        # Validação dos parâmetros
        if num_vms > len(self.DEFAULT_VMS):
            raise ValueError(f"O número de VMs ({num_vms}) não pode ser maior que o número de VMs pré-definidas ({len(self.DEFAULT_VMS)}).")
        if num_bucket_ranges > len(self.DEFAULT_BUCKETS):
            raise ValueError(f"O número de faixas de bucket ({num_bucket_ranges}) não pode ser maior que o número de faixas pré-definidas ({len(self.DEFAULT_BUCKETS)}).")

        self.params = {
            'tasks': num_tasks,
            'config': num_configs,
            'data': num_data,
            'vms': num_vms,
            'buckets': num_buckets,
            'bucket_ranges': num_bucket_ranges,
            'max_running_time': max_running_time,
            'max_financial_cost': max_financial_cost
        }
        self.use_integer_time = use_integer_time
        
        # Estruturas para armazenar os dados gerados
        self.tasks = []
        self.data_artifacts = {} # Usar um dict para acesso fácil aos tempos

    def _get_time(self, min_val, max_val):
        """ Retorna um valor de tempo (int ou float) baseado na configuração. """
        if self.use_integer_time:
            return random.randint(min_val, max_val)
        return random.uniform(min_val, max_val)

    def generate_summary_section(self):
        """ Gera a primeira linha/seção de resumo. """
        p = self.params
        header = "#<#tasks> <#config> <#data> <#vms> <#buckets> <#bucket_ranges> <max_running_time> <max_financial_cost>"
        line = f"{p['tasks']}\t{p['config']}\t{p['data']}\t{p['vms']}\t{p['buckets']}\t{p['bucket_ranges']}\t{p['max_running_time']}\t{p['max_financial_cost']}"
        return f"{header}\n{line}\n"

    def _generate_dag_and_data(self):
        """
        Gera a estrutura de tarefas (DAG), suas definições e os artefatos de dados.
        Esta é a lógica central para criar um workflow válido.
        """
        tasks_lines = []
        data_lines = []
        
        num_tasks = self.params['tasks']
        num_data = self.params['data']
        
        # Garante que há dados suficientes para o número de tarefas
        if num_data < num_tasks + 1:
            print(f"Aviso: O número de dados ({num_data}) é baixo para o número de tarefas ({num_tasks}). Ajustando para {num_tasks + 1}.")
            num_data = num_tasks + 1
            self.params['data'] = num_data

        available_data_ids = set()
        next_data_id = 1
        
        # 1. Criar dado inicial (static)
        initial_data_id = next_data_id
        available_data_ids.add(initial_data_id)
        
        read_time = self._get_time(1, 5) if self.use_integer_time else self._get_time(0.1, 0.5)
        self.data_artifacts[initial_data_id] = {'read_time': read_time, 'write_time': 0} # Static data has no write time
        data_lines.append(f"{initial_data_id}\t{random.randint(1000, 5000)}\t{read_time}\tNone\t1\t1\t[denethor_bucket]")
        next_data_id += 1

        # 2. Gerar tarefas sequencialmente para garantir a estrutura de DAG
        for task_id in range(1, num_tasks + 1):
            # Define o número de inputs e outputs
            num_inputs = random.randint(1, max(1, len(available_data_ids)))
            num_outputs = random.randint(1, 3)

            # Seleciona inputs dos dados já disponíveis
            inputs = random.sample(list(available_data_ids), num_inputs)
            
            # Gera novos IDs para os outputs, garantindo que não exceda o total
            outputs = []
            for _ in range(num_outputs):
                if next_data_id <= num_data:
                    outputs.append(next_data_id)
                    next_data_id += 1
                else:
                    break
            
            # Adiciona outputs aos dados disponíveis
            for data_id in outputs:
                available_data_ids.add(data_id)

            # Armazena a tarefa
            task_info = {
                'id': task_id,
                'activity_id': (task_id // 2) + 1,
                'cpu_time': self._get_time(1, 10) if self.use_integer_time else self._get_time(0.01, 0.5),
                'inputs': inputs,
                'outputs': outputs
            }
            self.tasks.append(task_info)
            
            # Formata a linha da tarefa
            tasks_lines.append(
                f"{task_id}\t{task_info['activity_id']}\t1\t{task_info['cpu_time']}\t{len(inputs)}\t[{','.join(map(str, inputs))}]\t{len(outputs)}\t[{','.join(map(str, outputs))}]"
            )

            # Gera as linhas de dados para os outputs
            for data_id in outputs:
                read_time = self._get_time(1, 5) if self.use_integer_time else self._get_time(0.1, 0.5)
                write_time = self._get_time(1, 3) if self.use_integer_time else self._get_time(0.05, 0.2)
                self.data_artifacts[data_id] = {'read_time': read_time, 'write_time': write_time}
                data_lines.append(f"{data_id}\t{random.randint(100, 2000)}\t{read_time}\t{write_time}\t0\t0\t[denethor_bucket]")

        # 3. Preenche com dados restantes, se houver (serão estáticos)
        while next_data_id <= num_data:
            data_id = next_data_id
            read_time = self._get_time(1, 5) if self.use_integer_time else self._get_time(0.1, 0.5)
            self.data_artifacts[data_id] = {'read_time': read_time, 'write_time': 0}
            data_lines.append(f"{data_id}\t{random.randint(1000, 5000)}\t{read_time}\tNone\t1\t1\t[denethor_bucket]")
            next_data_id += 1

        return tasks_lines, data_lines

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
        lines = random.sample(self.DEFAULT_VMS, self.params['vms'])
        # Reajusta o ID para ser sequencial
        lines = [f"{i+1}\t{line.split(maxsplit=1)[1]}" for i, line in enumerate(sorted(lines))]
        return f"{header}\n" + "\n".join(lines) + "\n"

    def generate_execution_results_section(self):
        """ Gera a seção de resultados da execução com base nas tarefas e dados gerados. """
        header = "#<task_id> <activity_id> <conf_id> <task_cost> <task_time_duration> <task_time_init> <task_time_cpu> <task_time_read> <task_time_write> <task_count>"
        lines = []
        
        for task in self.tasks:
            # Calcula tempos de leitura e escrita
            task_time_read = sum(self.data_artifacts[did]['read_time'] for did in task['inputs'])
            task_time_write = sum(self.data_artifacts[did]['write_time'] for did in task['outputs'])
            
            # Tempo de CPU é o mesmo da definição da tarefa para consistência
            task_time_cpu = task['cpu_time']
            
            # Calcula a duração total conforme a regra
            task_time_duration = task_time_read + task_time_write + task_time_cpu
            
            # Outros valores
            task_cost = task_time_duration * 0.000005 # Custo simulado
            task_time_init = 0.0
            task_count = random.randint(1, 10) # Quantidade de execuções agregadas
            
            lines.append(
                f"{task['id']}\t{task['activity_id']}\t1\t{task_cost:.10f}\t{task_time_duration:.4f}\t{task_time_init}\t{task_time_cpu:.4f}\t{task_time_read:.4f}\t{task_time_write:.4f}\t{task_count}"
            )
            
        return f"{header}\n" + "\n".join(lines) + "\n"

    def generate_buckets_section(self):
        """ Gera a seção de buckets de armazenamento. """
        header = "#<bucket_range_id> <size1_bytes> <size2_bytes> <cost_per_byte>"
        lines = self.DEFAULT_BUCKETS[:self.params['bucket_ranges']]
        return f"{header}\n" + "\n".join(lines) + "\n"

    def generate_workflow_file_content(self):
        """ Monta e retorna o conteúdo completo do arquivo de workflow. """
        
        # Gera as seções em ordem
        summary_section = self.generate_summary_section()
        tasks_section, data_section = self.generate_tasks_and_data_sections()
        vms_section = self.generate_vms_section()
        results_section = self.generate_execution_results_section()
        buckets_section = self.generate_buckets_section()

        # Concatena todas as seções
        full_content = (
            summary_section +
            "\n" +
            tasks_section +
            "\n" +
            data_section +
            "\n" +
            vms_section +
            "\n" +
            results_section +
            "\n" +
            buckets_section
        )
        
        return textwrap.dedent(full_content)

# --- Exemplo de Uso ---
if __name__ == '__main__':
    # --- PARÂMETROS DE ENTRADA ---
    # Defina aqui os valores para a geração do workflow
    
    # Seção de resumo
    NUM_TASKS = 20
    NUM_DATA_ARTIFACTS = 30
    NUM_VMS = 4
    NUM_BUCKET_RANGES = 3
    
    # Atributo para escolher o tipo de tempo
    USE_INTEGER_TIME = True # Mude para True se quiser tempos inteiros
    
    # --- FIM DOS PARÂMETROS ---

    print("Iniciando a geração do arquivo de workflow artificial...")
    
    generator = WorkflowGenerator(
        num_tasks=NUM_TASKS,
        num_data=NUM_DATA_ARTIFACTS,
        num_vms=NUM_VMS,
        num_bucket_ranges=NUM_BUCKET_RANGES,
        use_integer_time=USE_INTEGER_TIME
    )

    # Gera o conteúdo do arquivo
    workflow_content = generator.generate_workflow_file_content()

    # Salva o conteúdo em um arquivo
    file_name = f"generated_workflow_T{NUM_TASKS}_D{NUM_DATA_ARTIFACTS}.txt"
    with open(file_name, 'w') as f:
        f.write(workflow_content)

    print("-" * 50)
    print(f"Arquivo '{file_name}' gerado com sucesso!")
    print(f"Resumo da Geração:")
    print(f"  - Tarefas: {NUM_TASKS}")
    print(f"  - Dados: {generator.params['data']} (ajustado se necessário)")
    print(f"  - VMs: {NUM_VMS}")
    print(f"  - Tempos como {'Inteiros' if USE_INTEGER_TIME else 'Fracionários'}")
    print("-" * 50)
import random
from workflow_generator import WorkflowGenerator

class WorkflowGeneratorRandom(WorkflowGenerator):
    """
    Gera instâncias de workflow artificiais baseadas em parâmetros definidos.
    """

    def __init__(self, num_tasks, num_data, num_vms, num_configs=1, num_buckets=1, num_bucket_ranges=3,
                 max_running_time=100.0, max_financial_cost=0.1, use_integer_time=False):
        super().__init__(num_tasks, num_data, num_vms, num_configs, num_bucket_ranges, max_running_time, max_financial_cost, use_integer_time)

    # Métodos específicos ou sobrescritos devem ser mantidos abaixo
    def _generate_dag_and_data(self):
        """
        Gera a estrutura de tarefas (DAG), suas definições e os artefatos de dados.
        Esta é a lógica central para criar um workflow válido.
        """
        tasks_lines = []
        data_lines = []
        
        # Garante que há dados suficientes para o número de tarefas
        if self.num_data < self.num_tasks + 1:
            print(f"Aviso: O número de dados ({self.num_data}) é baixo para o número de tarefas ({self.num_tasks}). Ajustando para {self.num_tasks + 1}.")
            self.num_data = self.num_tasks + 1

        available_data_ids = set()
        next_data_id = 0

        # 1. Criar conjunto de dados iniciais (static)
        num_initial_data = random.randint(1, max(1, self.num_data // 2))
        for _ in range(num_initial_data):
            initial_data_id = f"d{next_data_id}"
            available_data_ids.add(initial_data_id)
            read_time = self._get_time(1, 5) if self.use_integer_time else self._get_time(0.1, 0.5)
            self.data_artifacts[initial_data_id] = {'read_time': read_time, 'write_time': 0} # Static data has no write time
            data_lines.append(f"{initial_data_id}\t{random.randint(1000, 5000)}\t{read_time}\tNone\t1\t1\t[denethor_bucket]")
            next_data_id += 1

        # 2. Gerar tarefas sequencialmente para garantir a estrutura de DAG
        for task_id in range(self.num_tasks):
            # Define o número de inputs e outputs
            num_inputs = random.randint(1, max(1, len(available_data_ids)))
            num_outputs = random.randint(1, 3)

            # Seleciona inputs dos dados já disponíveis
            inputs = random.sample(list(available_data_ids), num_inputs)
            
            # Gera novos IDs para os outputs, garantindo que não exceda o total
            outputs = []
            for _ in range(num_outputs):
                if next_data_id < self.num_data:
                    output_id = f"d{next_data_id}"
                    outputs.append(output_id)
                    next_data_id += 1
                else:
                    break
            # Adiciona outputs aos dados disponíveis
            for data_id in outputs:
                available_data_ids.add(data_id)

            # Armazena a tarefa
            task_info = {
                'id': f"t{task_id}",
                'activity_id': (task_id // 2) + 1,
                'cpu_time': self._get_time(1, 10) if self.use_integer_time else self._get_time(0.01, 0.5),
                'inputs': inputs,
                'outputs': outputs
            }
            self.tasks.append(task_info)

            # Formata a linha da tarefa
            tasks_lines.append(
                f"{task_info['id']}\t{task_info['activity_id']}\t1\t{task_info['cpu_time']}\t{len(inputs)}\t[{','.join(map(str, inputs))}]\t{len(outputs)}\t[{','.join(map(str, outputs))}]"
            )

            # Gera as linhas de dados para os outputs
            for data_id in outputs:
                read_time = self._get_time(1, 5) if self.use_integer_time else self._get_time(0.1, 0.5)
                write_time = self._get_time(1, 3) if self.use_integer_time else self._get_time(0.05, 0.2)
                self.data_artifacts[data_id] = {'read_time': read_time, 'write_time': write_time}
                data_lines.append(f"{data_id}\t{random.randint(100, 2000)}\t{read_time}\t{write_time}\t0\t0\t[denethor_bucket]")

        # 3. Preenche com dados restantes, se houver (serão estáticos)
        while next_data_id < self.num_data:
            data_id = f"d{next_data_id}"
            read_time = self._get_time(1, 5) if self.use_integer_time else self._get_time(0.1, 0.5)
            self.data_artifacts[data_id] = {'read_time': read_time, 'write_time': 0}
            data_lines.append(f"{data_id}\t{random.randint(1000, 5000)}\t{read_time}\tNone\t1\t1\t[denethor_bucket]")
            next_data_id += 1

        return tasks_lines, data_lines


import os, random
from workflow_generator import WorkflowGenerator

class WorkflowGeneratorUserDefined(WorkflowGenerator):
    def __init__(self, workflow_id, num_tasks, num_data, task_defs, output_dir, num_vms=2, num_configs=2, num_bucket_ranges=3, use_integer_time=True):
        super().__init__(
            num_tasks=num_tasks,
            num_data=num_data,
            num_vms=num_vms,
            num_configs=num_configs,
            num_bucket_ranges=num_bucket_ranges,
            use_integer_time=use_integer_time
        )
        self.workflow_id = workflow_id
        self.task_defs = task_defs
        self.output_dir = output_dir

    def _generate_dag_and_data(self):
        tasks_lines = []
        data_lines = []
        self.tasks = []
        self.data_artifacts = {}
        used_data_ids = set()
        
        # Tasks
        for task in self.task_defs:
            cpu_time = self._get_time(1, 10) if self.use_integer_time else self._get_time(0.01, 0.5)
            tid_num = int(task['id'][1:]) if task['id'].startswith('t') and task['id'][1:].isdigit() else task['id']
            activity_id = (int(tid_num) // 2) + 1 if isinstance(tid_num, int) else 1
            self.tasks.append({
                'id': task['id'],
                'activity_id': activity_id,
                'cpu_time': cpu_time,
                'inputs': [d for d in task['inputs']],
                'outputs': [d for d in task['outputs']]
            })
            tasks_lines.append(
                f"{task['id']}\t{activity_id}\t1\t{cpu_time}\t{len(task['inputs'])}\t[{','.join(task['inputs'])}]\t{len(task['outputs'])}\t[{','.join(task['outputs'])}]"
            )
            for did in task['inputs'] + task['outputs']:
                if did not in used_data_ids:
                    used_data_ids.add(did)
                    read_time = self._get_time(1, 5) if self.use_integer_time else self._get_time(0.1, 0.5)
                    write_time = self._get_time(1, 3) if self.use_integer_time else self._get_time(0.05, 0.2)
                    self.data_artifacts[did] = {'read_time': read_time, 'write_time': write_time}
                    data_lines.append(f"{did}\t{random.randint(100, 2000)}\t{read_time}\t{write_time}\t0\t0\t[denethor_bucket]")
        
        return tasks_lines, data_lines

def parse_user_defined_workflows(input_file):
    workflows = []
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    i = 0
    while i < len(lines):
        if lines[i].startswith("WORKFLOW_ID:"):
            workflow_id = lines[i].split(":")[1].strip()
            i += 1
            num_tasks = int(lines[i].split(":")[1].strip())
            i += 1
            num_data = int(lines[i].split(":")[1].strip())
            i += 1
            assert lines[i] == "---"
            i += 1
            task_defs = []
            while i < len(lines) and not lines[i].startswith("--------------------------------"):
                line = lines[i]
                if line:
                    tid, rest = line.split(":")
                    tid = tid.strip()
                    inputs, outputs = rest.split("->")
                    inputs = [x.strip() for x in inputs.strip().split(",") if x.strip()]
                    outputs = [x.strip() for x in outputs.strip().split(",") if x.strip()]
                    task_defs.append({'id': tid, 'inputs': inputs, 'outputs': outputs})
                i += 1
            workflows.append({
                'workflow_id': workflow_id,
                'num_tasks': num_tasks,
                'num_data': num_data,
                'task_defs': task_defs
            })
        i += 1
    return workflows

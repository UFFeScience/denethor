import os, random
from workflow_generator import WorkflowGenerator

class WorkflowGeneratorUserDefined(WorkflowGenerator):
    def __init__(self, workflow_id, num_tasks, num_data, task_defs, output_dir, num_vms=2, num_configs=2, num_bucket_ranges=3, use_integer_time=True, task_prefix_replace=None, data_prefix_replace=None):
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
        self.task_prefix_replace = task_prefix_replace  # Dict: {'old': 't', 'new': '1'}
        self.data_prefix_replace = data_prefix_replace  # Dict: {'old': 'd', 'new': '9'}

    def _replace_id_prefix(self, id_str, prefix_config):
        """Replace ID prefix if configured"""
        if not prefix_config:
            return id_str
        old_prefix = prefix_config.get('old')
        new_prefix = prefix_config.get('new')
        if old_prefix and new_prefix and id_str.startswith(old_prefix):
            return new_prefix + id_str[len(old_prefix):]
        return id_str

    def _generate_dag_and_data(self):
        tasks_lines = []
        data_lines = []
        self.tasks = []
        self.data_artifacts = {}
        used_data_ids = set()
        
        # Tasks
        for task in self.task_defs:
            cpu_time = self._get_time(1, 10) if self.use_integer_time else self._get_time(0.01, 0.5)
            task_id = self._replace_id_prefix(task['id'], self.task_prefix_replace)
            tid_num = int(task_id[1:]) if task_id[1:].isdigit() else task_id
            activity_id = (int(tid_num) // 2) + 1 if isinstance(tid_num, int) else 1
            
            # Replace prefixes in inputs and outputs
            inputs = [self._replace_id_prefix(d, self.data_prefix_replace) for d in task['inputs']]
            outputs = [self._replace_id_prefix(d, self.data_prefix_replace) for d in task['outputs']]
            
            self.tasks.append({
                'id': task_id,
                'activity_id': activity_id,
                'cpu_time': cpu_time,
                'inputs': inputs,
                'outputs': outputs
            })
            tasks_lines.append(
                f"{task_id}\t{activity_id}\t1\t{cpu_time:.4f}\t{len(inputs)}\t[{','.join(inputs)}]\t{len(outputs)}\t[{','.join(outputs)}]"
            )
            for did in inputs + outputs:
                if did not in used_data_ids:
                    used_data_ids.add(did)
                    read_time = self._get_time(1, 5) if self.use_integer_time else self._get_time(0.1, 0.5)
                    write_time = self._get_time(1, 3) if self.use_integer_time else self._get_time(0.05, 0.2)
                    self.data_artifacts[did] = {'read_time': read_time, 'write_time': write_time}
                    data_lines.append(f"{did}\t{random.randint(100, 2000)}\t{read_time:.4f}\t{write_time:.4f}\t0\t0\t[denethor_bucket]")
        
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

import os, random
import re
from .workflow_gen_model import WorkflowGeneratorModel

class WorkflowGeneratorUserDefined(WorkflowGeneratorModel):
    def __init__(self, workflow_id, num_tasks, num_data, task_defs, output_dir, num_vms=2, num_configs=2, num_bucket_ranges=3, use_integer_time=True, task_prefix_replace=None, data_prefix_replace=None, task_id_offset=0, data_id_offset=0):
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
        self.task_id_offset = task_id_offset
        self.data_id_offset = data_id_offset

    def _process_id(self, id_str, prefix_config, offset):
        """Replace ID prefix and apply offset if configured"""
        result = id_str
        if prefix_config:
            old_prefix = prefix_config.get('old')
            new_prefix = prefix_config.get('new')
            if old_prefix is not None and new_prefix is not None and result.startswith(old_prefix):
                result = new_prefix + result[len(old_prefix):]
        
        if offset:
            match = re.search(r"(\d+)$", result)
            if match:
                num = int(match.group(1)) + offset
                result = result[:match.start()] + str(num)
        return result

    def _build_tasks_and_data_model(self):
        tasks = []
        data_artifacts = {}
        used_data_ids = set()
        produced_data_ids = set()
        
        # Tasks
        for task in self.task_defs:
            cpu_time = self._get_time(1, 10) if self.use_integer_time else self._get_time(0.01, 0.5)
            task_id = self._process_id(task['id'], self.task_prefix_replace, self.task_id_offset)
            
            match = re.search(r"(\d+)$", task_id)
            tid_num = int(match.group(1)) if match else None
            activity_id = (tid_num // 2) + 1 if tid_num is not None else 1
            
            # Replace prefixes in inputs and outputs
            inputs = [self._process_id(d, self.data_prefix_replace, self.data_id_offset) for d in task['inputs']]
            outputs = [self._process_id(d, self.data_prefix_replace, self.data_id_offset) for d in task['outputs']]
            
            tasks.append({
                'id': task_id,
                'activity_id': activity_id,
                'cpu_time': cpu_time,
                'inputs': inputs,
                'outputs': outputs
            })

            used_data_ids.update(inputs)
            used_data_ids.update(outputs)
            produced_data_ids.update(outputs)

        # Constrói os metadados com semântica explícita:
        # dados produzidos -> dinâmicos (write_time>0)
        # dados apenas consumidos -> estáticos (write_time=None)
        for did in used_data_ids:
            read_time = self._get_time(1, 5) if self.use_integer_time else self._get_time(0.1, 0.5)
            write_time = (
                self._get_time(1, 3) if self.use_integer_time else self._get_time(0.05, 0.2)
            ) if did in produced_data_ids else None
            data_artifacts[did] = {
                "size_bytes": random.randint(100, 2000),
                "read_time": read_time,
                "write_time": write_time,
            }

        return tasks, data_artifacts

def parse_user_defined_workflows(input_file):
    workflows = []
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    i = 0
    while i < len(lines):
        if lines[i].startswith("WORKFLOW_ID:"):
            workflow_id = lines[i].split(":", 1)[1].strip()
            i += 1
            
            num_tasks = 0
            num_data = 0
            pattern = ""
            comment_lines = []
            
            in_comment = False
            while i < len(lines) and lines[i] != "---":
                line = lines[i]
                if line.startswith("TASKS:"):
                    num_tasks = int(line.split(":", 1)[1].strip())
                    in_comment = False
                elif line.startswith("DATA:"):
                    num_data = int(line.split(":", 1)[1].strip())
                    in_comment = False
                elif line.startswith("PATTERN:"):
                    pattern = line.split(":", 1)[1].strip()
                    in_comment = False
                elif line.startswith("COMMENT:"):
                    comment_text = line.split(":", 1)[1].strip()
                    if comment_text:
                        comment_lines.append(comment_text)
                    in_comment = True
                elif in_comment:
                    comment_lines.append(line)
                i += 1
            
            comment = "\n".join(comment_lines)
            
            if i < len(lines) and lines[i] == "---":
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
                'pattern': pattern,
                'comment': comment,
                'task_defs': task_defs
            })
        i += 1
    return workflows

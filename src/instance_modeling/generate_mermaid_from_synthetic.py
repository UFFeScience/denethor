import os
import re

input_file = "/home/marcello/Documents/denethor/resources/data/instance_files/synthetic/synthetic_user_defined/my_synthetic_instances_definition.txt"
output_dir = "/home/marcello/Documents/denethor/resources/data/instance_files/synthetic/synthetic_user_defined/mermaid"

os.makedirs(output_dir, exist_ok=True)

with open(input_file, 'r') as f:
    content = f.read()

workflows = content.split('--------------------------------')

for wf in workflows:
    wf = wf.strip()
    if not wf:
        continue
    
    lines = wf.split('\n')
    wf_id_line = lines[0]
    
    # Example line: WORKFLOW_ID: Synthetic_007
    if ':' not in wf_id_line:
        continue
        
    wf_id = wf_id_line.split(':')[1].strip()
    
    try:
        num_str = wf_id.split('_')[1]
        num = int(num_str)
    except Exception:
        continue
        
    prefix = f"S{num}"
    
    # Extract tasks and data
    tasks = set()
    data = set()
    
    edges_from_data = {} # dX -> list of tY
    edges_from_task = {} # tX -> list of dY
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('---') or line.startswith('WORKFLOW_ID') or line.startswith('TASKS') or line.startswith('DATA'):
            continue
            
        # e.g., t0: d0,d1 -> d2
        if ':' in line and '->' in line:
            task_part, rest = line.split(':')
            t_id = task_part.strip()
            tasks.add(t_id)
            
            in_data_str, out_data_str = rest.split('->')
            in_data = [d.strip() for d in in_data_str.split(',') if d.strip()]
            out_data = [d.strip() for d in out_data_str.split(',') if d.strip()]
            
            for d in in_data:
                data.add(d)
                if d not in edges_from_data:
                    edges_from_data[d] = []
                edges_from_data[d].append(t_id)
                
            for d in out_data:
                data.add(d)
                if t_id not in edges_from_task:
                    edges_from_task[t_id] = []
                edges_from_task[t_id].append(d)

    # Generate Mermaid
    mermaid_lines = []
    mermaid_lines.append("---")
    mermaid_lines.append("config:")
    mermaid_lines.append("  layout: dagre")
    mermaid_lines.append("  theme: redux")
    mermaid_lines.append("  look: neo")
    mermaid_lines.append("---")
    mermaid_lines.append("flowchart LR")
    mermaid_lines.append(f' subgraph Synthetic_{num}["{wf_id}"]')
    mermaid_lines.append("    direction LR")
    
    # Note: formatting dX and tX
    for d in sorted(data, key=lambda x: int(x[1:])):
        d_num = d[1:]
        mermaid_lines.append(f'        {prefix}_{d}(("d_9{d_num}"))')
        
    for t in sorted(tasks, key=lambda x: int(x[1:])):
        t_num = t[1:]
        mermaid_lines.append(f'        {prefix}_{t}("t_1{t_num}")')

    mermaid_lines.append("  end")
    
    for d in sorted(edges_from_data.keys(), key=lambda x: int(x[1:])):
        targets = edges_from_data[d]
        targets_str = " & ".join([f"{prefix}_{t}" for t in targets])
        mermaid_lines.append(f"    {prefix}_{d} --> {targets_str}")

    for t in sorted(edges_from_task.keys(), key=lambda x: int(x[1:])):
        targets = edges_from_task[t]
        targets_str = " & ".join([f"{prefix}_{d}" for d in targets])
        mermaid_lines.append(f"    {prefix}_{t} --> {targets_str}")

    output_path = os.path.join(output_dir, f"Synthetic_{num:03d}.mermaid")
    with open(output_path, 'w') as f:
        f.write('\n'.join(mermaid_lines))
        f.write('\n')
    
    print(f"Generated {output_path}")


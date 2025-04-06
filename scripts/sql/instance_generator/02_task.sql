--#<task_id> <activity_id> <task_type__0-VM__1-VM_FX> <vm_cpu_time> <n_input> [<id_input>...] <n_output> [<id_output>...]
SELECT DISTINCT 
	ta.task_id,
	ta.activity_id,
	ta.task_type,
	99999 AS vm_cpu_time, --tempo base em vm,
	ta.consumed_files_count AS n_input,
	'[' || ta.consumed_files_list || ']' AS input_list,
	ta.produced_files_count AS n_output,
	'[' || ta.produced_files_list || ']' AS output_list
FROM service_execution se
JOIN workflow_execution we ON se.we_id = we.we_id
JOIN vw_service_execution_task st ON se.se_id = st.se_id
JOIN vw_task ta ON st.task_id = ta.task_id
WHERE we.execution_tag in ('[wetag]')
ORDER BY ta.activity_id, ta.task_id
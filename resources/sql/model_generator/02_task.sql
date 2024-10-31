--#<task_id> <task_type__0-VM__1-FX> <vm_cpu_time> <n_input> [<id_input>...] <n_output> [<id_output>...]
SELECT DISTINCT 
	ta.task_id, --se.se_id, se.activity_id,
	task_type,
	99999 AS vm_cpu_time, --tempo base em vm,
	ta.input_count AS n_input,
	'[' || ta.input_list || ']' AS input_list,
	ta.output_count AS n_output,
	'[' || ta.output_list || ']' AS output_list
FROM service_execution se
JOIN task ta on se.task_id = ta.task_id
WHERE se.workflow_execution_id in ('weid_1724184708846')--, 'weid_1724433692051')
ORDER BY task_id
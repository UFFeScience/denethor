--#<task_id> <activity_id> <task_type__0-VM__1-VM_FX> <vm_cpu_time> <n_input> [<id_input>...] <n_output> [<id_output>...]
WITH vm_base_time AS (
	SELECT DISTINCT 
		se.se_id, 
		se.we_id,
		we.execution_tag,
		pc.provider_id,
		pr.provider_tag,
		ta.task_id,
		se.activity_id,
		st.statistics_id,
		st.statistics_name, 
		es.value_float as vm_cpu_time
	FROM service_execution se
	JOIN provider_configuration pc on pc.conf_id = se.provider_conf_id
	JOIN provider pr on pr.provider_id = pc.provider_id
	JOIN workflow_execution we ON we.we_id = se.we_id
	JOIN vw_service_execution_task sxt ON sxt.se_id = se.se_id
	JOIN vw_task ta ON ta.task_id = sxt.task_id
	JOIN execution_statistics es ON es.se_id = se.se_id
	JOIN statistics st ON st.statistics_id = es.statistics_id
	WHERE we.execution_tag in ([wetag_vm])
		 AND pr.provider_tag = 'aws_ec2'
		 AND st.statistics_name IN ('tree_duration', 'subtree_duration', 'maf_db_creator_duration', 'maf_db_aggregator_duration')
 )
SELECT DISTINCT 
	ta.task_id,
	ta.activity_id,
	ta.task_type,
	vm.vm_cpu_time,
	ta.input_count AS n_input,
	'[' || ta.input_list || ']' AS input_list,
	ta.output_count AS n_output,
	'[' || ta.output_list || ']' AS output_list
FROM service_execution se
JOIN workflow_execution we ON se.we_id = we.we_id
JOIN vw_service_execution_task st ON se.se_id = st.se_id
JOIN vw_task ta ON st.task_id = ta.task_id
JOIN vm_base_time vm ON ta.task_id = vm.task_id
WHERE we.execution_tag in ([wetag_fx])
ORDER BY ta.activity_id, ta.task_id;
-- workflow executions with provider
select distinct we_id, workflow_start_time, workflow_end_time, workflow_duration, workflow_input_count, provider_tag, provider_memory_mb
from vw_service_execution_detail
where we_id >= 135
order by we_id;


-- workflow executions
SELECT * FROM workflow_execution we
where we_id >= 135
order by we_id;


-- arquivos de entrada
SELECT distinct input_count, input_list FROM workflow_execution we
where we_id between 135 and 189
order by input_count;


-- arquivos de entrada para execução em VM baseados na execução em FX
WITH basic_data AS (
    SELECT DISTINCT input_count, input_list
    FROM workflow_execution we
    WHERE we_id between 135 and 189
    ORDER BY input_count
)
SELECT json_object_agg(
    input_count,
    input_list::json
) AS result
FROM basic_data;


-- Exibir os dados de execução do workflow
SELECT DISTINCT
    we_id,
    execution_tag,
    workflow_start_time,
    workflow_duration,
    workflow_input_count,
    provider_id,
    provider_name,
    provider_memory_mb
FROM vw_service_execution_detail
ORDER BY we_id;



--execução em vm: wetag_1744507705125
--WETAG = []

--tentando obter vm_cpu_time
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
	WHERE we.execution_tag IN ('wetag_1745013809114') 
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
WHERE we.execution_tag in ('wetag_1744914790201')
ORDER BY ta.activity_id, ta.task_id;





--statistics
SELECT DISTINCT 
sei.se_id, sei.we_id, sei.workflow_input_count, sei.execution_tag,  sei.provider_id, sei.provider_name, ta.task_id, sei.activity_id, sei.activity_name, 
stat.statistics_id, stat.statistics_name, 
substr(ta.consumed_files_list,1,30) in_files, 
substr(ta.produced_files_list,1,30) out_files, 
concat(es.value_float, es.value_integer, substr(es.value_string, 1, 100)) as value
FROM vw_service_execution_info sei
LEFT OUTER JOIN vw_service_execution_task st ON sei.se_id = st.se_id
LEFT OUTER JOIN vw_task ta ON st.task_id = ta.task_id
LEFT OUTER JOIN execution_statistics es ON es.se_id = sei.se_id
LEFT OUTER JOIN "statistics" stat ON stat.statistics_id = es.statistics_id
WHERE execution_tag in ('wetag_1744914790201')
ORDER BY ta.task_id, sei.provider_id;



--files
SELECT sei.execution_tag, COUNT(*) as total_files, COUNT(*) * 5 as total_files_for_all_configs, COUNT(*) * 5 / 1000 * 0.007 * 5.90 as estimated_cost
FROM execution_file ef
JOIN vw_service_execution_info sei on sei.se_id = ef.se_id
WHERE execution_tag in ('wetag_1744754708329', 'wetag_1744757716148')
GROUP BY sei.execution_tag;


--tasks
SELECT DISTINCT 
	we.we_id, 
	we.execution_tag, 
	we.input_count, 
	COUNT(*) as n_tasks
FROM vw_task ta 
LEFT OUTER JOIN vw_service_execution_task st ON st.task_id = ta.task_id
LEFT OUTER JOIN service_execution se ON se.se_id = st.se_id
LEFT OUTER JOIN workflow_execution we ON we.we_id = se.we_id
WHERE we.we_id >= 68
GROUP BY we.execution_tag, we.input_count, we.we_id 
;


select
se.se_id, se.we_id, we.execution_tag, p.provider_name, pc.memory_mb, se.activity_id, f.file_id, f.file_name, f.file_size, ef.transfer_type, ef.transfer_duration
from service_execution se
join workflow_execution we on se.we_id = we.we_id
join provider_configuration pc on pc.conf_id = se.provider_conf_id
join provider p on p.provider_id = pc.provider_id
join execution_file ef on ef.se_id = se.se_id
join file f on f.file_id = ef.file_id
where we.we_id = 135
order by f.file_id
;


--CALL delete_execution_data('wetag_xxxxxxxxxxxx');



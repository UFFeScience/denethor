SELECT * FROM vw_service_execution_info_last ORDER BY se_id;

SELECT *
FROM service_execution
WHERE
    workflow_execution_id = 'weid_1729872039000';

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
FROM vw_service_execution_info
ORDER BY we_id;



--execução em vm: wetag_1744507705125
--WETAG = []

--tentando obter vm_cpu_time
WITH vm_base_time AS (
	SELECT DISTINCT 
		se1.se_id, 
		se1.we_id,
		we1.execution_tag,
		pc1.provider_id,
		pr1.provider_tag,
		ta1.task_id,
		se1.activity_id,
		stat1.statistics_id,
		stat1.statistics_name, 
		es1.value_float as vm_cpu_time
	FROM service_execution se1
	JOIN provider_configuration pc1 on pc1.conf_id = se1.provider_conf_id
	JOIN provider pr1 on pr1.provider_id = pc1.provider_id
	JOIN workflow_execution we1 ON se1.we_id = we1.we_id
	JOIN vw_service_execution_task st1 ON se1.se_id = st1.se_id
	JOIN vw_task ta1 ON st1.task_id = ta1.task_id
	JOIN execution_statistics es1 ON es1.se_id = se1.se_id
	JOIN "statistics" stat1 ON stat1.statistics_id = es1.statistics_id
	WHERE we1.execution_tag in ('wetag_1744507705125') 
		 AND pr1.provider_tag = 'aws_ec2'
		 AND stat1.statistics_name like '%duration%'
 )
SELECT DISTINCT 
	ta.task_id,
	ta.activity_id,
	ta.task_type,
	vm.vm_cpu_time,
	ta.consumed_files_count AS n_input,
	'[' || ta.consumed_files_list || ']' AS input_list,
	ta.produced_files_count AS n_output,
	'[' || ta.produced_files_list || ']' AS output_list
FROM service_execution se
JOIN workflow_execution we ON se.we_id = we.we_id
JOIN vw_service_execution_task st ON se.se_id = st.se_id
JOIN vw_task ta ON st.task_id = ta.task_id
JOIN vm_base_time vm ON ta.task_id = vm.task_id
WHERE we.execution_tag in ('wetag_1743638228939')
ORDER BY ta.activity_id, ta.task_id;





--tentando obter vm_cpu_time a partir de task e service_execution2
WITH vm_base_time AS (
	SELECT DISTINCT 
		se1.se_id, 
		se1.we_id,
		we1.execution_tag,
		pc1.provider_id,
		pr1.provider_tag,
		ta1.task_id,
		se1.activity_id,
		stat1.statistics_id,
		stat1.statistics_name, 
		es1.value_float as vm_cpu_time
	FROM service_execution2 se1
	JOIN provider_configuration pc1 on pc1.conf_id = se1.provider_conf_id
	JOIN provider pr1 on pr1.provider_id = pc1.provider_id
	JOIN workflow_execution we1 ON se1.we_id = we1.we_id
	JOIN task ta1 ON se1.task_id = ta1.task_id
	JOIN execution_statistics es1 ON es1.se_id = se1.se_id
	JOIN "statistics" stat1 ON stat1.statistics_id = es1.statistics_id
	WHERE we1.execution_tag in ('wetag_1744507705125') 
		 AND pr1.provider_tag = 'aws_ec2'
		 AND stat1.statistics_name like '%duration%'
 )
SELECT DISTINCT 
	ta.task_id,
	ta.activity_id,
	ta.task_type,
	vm.vm_cpu_time*0.001 AS vm_cpu_time,
	ta.input_count AS n_input,
	'[' || ta.input_list || ']' AS input_list,
	ta.output_count AS n_output,
	'[' || ta.output_list || ']' AS output_list
FROM service_execution2 se
JOIN workflow_execution we ON se.we_id = we.we_id
JOIN task ta ON se.task_id = ta.task_id
JOIN vm_base_time vm ON ta.task_id = vm.task_id
WHERE we.execution_tag in ('wetag_1743638228939')
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
WHERE execution_tag in ('wetag_1743638228939', 'wetag_1744507705125')
ORDER BY ta.task_id, sei.provider_id;



--files
SELECT sei.execution_tag, COUNT(*) as total_files, COUNT(*) * 5 as total_files_for_all_configs, COUNT(*) * 5 / 1000 * 0.007 * 5.90 as estimated_cost
FROM execution_file ef
JOIN vw_service_execution_info sei on sei.se_id = ef.se_id
WHERE execution_tag in ('wetag_1744754708329', 'wetag_1744757716148')
GROUP BY sei.execution_tag;


-- tree and subtree files with transfer_time
SELECT f.file_id, f.file_name, f.file_size, ef.file_id, ef.se_id, ef.transfer_duration, ef.transfer_type, we.we_id, we.execution_tag, se.*
FROM file f
JOIN execution_file ef ON f.file_id = ef.file_id
JOIN service_execution se ON se.se_id = ef.se_id
JOIN workflow_execution we ON we.we_id = se.we_id
--WHERE execution_tag ='wetag_1744861181586'
WHERE execution_tag ='wetag_1744912694622' and se.activity_id = 3;

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

select * from vw_task ta;


select * from workflow_execution we
--where we.we_id >= 68
where we.execution_tag = 'wetag_1744925395446';

select * from vw_service_execution_info
order by se_id desc


select * from workflow_execution;


select * from file where file_name = 'mafdb_6f7a2b1116e6a791f68a03367473294792b679a6357b6789f3f993b1f83e2e80.json'

CALL delete_execution_data('wetag_1744925395446');


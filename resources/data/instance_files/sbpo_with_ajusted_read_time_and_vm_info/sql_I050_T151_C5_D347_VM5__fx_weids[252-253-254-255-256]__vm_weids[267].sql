--->scripts/sql/instance_generator/01_totals.sql
--->weids_fx:[252, 253, 254, 255, 256]
--->weids_vm:[267]
--->Generated at 2025-05-30 13:50:01

#<#tasks> <#config> <#data> <#vms> <#buckets> <#bucket_ranges> <max_running_time> <max_financial_cost>
SELECT 
	(SELECT count(distinct st.task_id) AS _tasks_count
		FROM service_execution se
		JOIN workflow_execution we ON se.we_id = we.we_id
		JOIN vw_service_execution_task st ON se.se_id = st.se_id
		WHERE we.we_id in (252,253,254,255,256)
	),
	(SELECT count(pc.conf_id) AS _configs_count
		FROM provider_configuration pc
		JOIN provider pr on pc.provider_id = pr.provider_id
		WHERE pr.provider_tag = 'aws_lambda'
	),
	(SELECT count(distinct ef.file_id ) AS _files_count
		FROM service_execution se
		JOIN workflow_execution we ON se.we_id = we.we_id 
		JOIN execution_file ef ON ef.se_id = se.se_id 
		WHERE we.we_id in (252,253,254,255,256)
	),
	(SELECT count(*) AS _vms_count
		FROM vm_configurations
	),
	(SELECT count(distinct fi.file_bucket ) AS _buckets_count
		FROM service_execution se
		JOIN workflow_execution we ON se.we_id = we.we_id
		JOIN execution_file ef ON ef.se_id = se.se_id
		JOIN file fi ON fi.file_id = ef.file_id
		WHERE we.we_id in (252,253,254,255,256)
	),
	(SELECT count(*) AS _bucket_ranges_count
		FROM bucket_ranges
	),
	(SELECT max(t.max_workflow_duration) AS _max_running_time
		FROM (
			SELECT 
				we.we_id,
				se.provider_conf_id,
				sum(se.duration*0.001) AS max_workflow_duration,
				count(*) AS task_count
			FROM service_execution se
			JOIN workflow_execution we ON se.we_id = we.we_id
			WHERE we.we_id in (252,253,254,255,256)
			GROUP BY we.we_id, se.provider_conf_id
			ORDER BY we.we_id
		) t
	),
	(SELECT max(t.max_workflow_cost) AS _max_financial_cost
		FROM (
			SELECT 
				we.we_id,
				se.provider_conf_id,
				--cost = duration (s) x memory (gb) x computation cost x fixed cost
				to_char(sum(se.duration*0.001*se.memory_size*0.0009765625*0.0000166667 + 0.0000002),'fm999990D9999999999999999') AS max_workflow_cost,		
				count(*) AS task_count
			FROM service_execution se
			JOIN workflow_execution we ON se.we_id = we.we_id
			WHERE we.we_id in (252,253,254,255,256)
			GROUP BY we.we_id, se.provider_conf_id
			ORDER BY we.we_id
		) t
	);
;



--->scripts/sql/instance_generator/02_task.sql
--->weids_fx:[252, 253, 254, 255, 256]
--->weids_vm:[267]
--->Generated at 2025-05-30 13:50:31

#<task_id> <activity_id> <task_type__0-VM__1-VM_FX> <vm_cpu_time> <n_input> [<id_input>...] <n_output> [<id_output>...]
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
		es.value_float*0.001 as vm_cpu_time
	FROM service_execution se
	JOIN provider_configuration pc on pc.conf_id = se.provider_conf_id
	JOIN provider pr on pr.provider_id = pc.provider_id
	JOIN workflow_execution we ON we.we_id = se.we_id
	JOIN vw_service_execution_task sxt ON sxt.se_id = se.se_id
	JOIN vw_task ta ON ta.task_id = sxt.task_id
	JOIN execution_statistics es ON es.se_id = se.se_id
	JOIN statistics st ON st.statistics_id = es.statistics_id
	WHERE we.we_id in (267)
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
WHERE we.we_id in (252,253,254,255,256)
ORDER BY ta.activity_id, ta.task_id;



--->scripts/sql/instance_generator/03_data.sql
--->weids_fx:[252, 253, 254, 255, 256]
--->weids_vm:[267]
--->Generated at 2025-05-30 13:50:31

#<data_id> <data_size> <read_time_avg> <write_time_avg> <is_static> <n_source_devices> [<device_id>...]
--is_static: 0-dynamic / 1-static
--n_source_devices: 0 if dynamic
WITH 
produced_file AS (
	SELECT
		ef.file_id AS produced_file_id,
		CAST(avg(f.file_size) AS INTEGER) AS produced_file_size,
		avg(ef.transfer_duration)*0.001 AS write_time_avg
	FROM execution_file ef
	JOIN file f ON f.file_id = ef.file_id
	JOIN service_execution se ON se.se_id = ef.se_id
	JOIN workflow_execution we ON se.we_id = we.we_id
	WHERE ef.transfer_type = 'produced' AND we.we_id in (252,253,254,255,256)
	GROUP BY ef.file_id
),
consumed_files AS (
	SELECT
		ef.file_id AS consumed_file_id,
		CAST(avg(f.file_size) AS INTEGER) AS consumed_file_size,
		avg(ef.transfer_duration)*0.001 AS read_time_avg
	FROM execution_file ef
	JOIN file f ON f.file_id = ef.file_id
	JOIN service_execution se ON se.se_id = ef.se_id
	JOIN workflow_execution we ON se.we_id = we.we_id
	WHERE ef.transfer_type = 'consumed' AND we.we_id in (252,253,254,255,256)
	GROUP BY ef.file_id
)
SELECT 
	COALESCE(consumed_file_id, produced_file_id) AS data_id,
	COALESCE(consumed_file_size, produced_file_size) AS data_size,
	read_time_avg,
	write_time_avg,
	CASE 
		WHEN produced_file_id IS NOT NULL THEN 0 --dynamic
		WHEN produced_file_id IS NULL AND consumed_file_id IS NOT NULL THEN 1 --static
		ELSE -1
	END AS is_static,
	CASE 
		WHEN produced_file_id IS NOT NULL THEN 0 --dynamic has zero sources
		WHEN produced_file_id IS NULL AND consumed_file_id IS NOT NULL THEN 1 --static has one source
		ELSE -1
	END AS n_source_devices,
	'[denethor_bucket]' AS device_list
FROM consumed_files 
FULL OUTER JOIN  produced_file ON produced_file_id = consumed_file_id	
ORDER BY consumed_file_id;



--->scripts/sql/instance_generator/04_vm_info.sql
--->weids_fx:[252, 253, 254, 255, 256]
--->weids_vm:[267]
--->Generated at 2025-05-30 13:50:31

#<vm_id> <cpu_slowdown> <cost_per_second> <storage_mb> <bandwidth_mbps>
SELECT 
    vm_id,
    cpu_slowdown,
    cost AS cost_per_second,
    storage AS storage_mb,
    bandwidth AS bandwidth_mbps
FROM vm_configurations
ORDER BY vm_id
;



--->scripts/sql/instance_generator/05_time_cost_matrix.sql
--->weids_fx:[252, 253, 254, 255, 256]
--->weids_vm:[267]
--->Generated at 2025-05-30 13:50:45

#<task_id> <activity_id> <conf_id> <task_cost> <task_time_duration> <task_time_init> <task_time_cpu> <task_time_read> <task_time_write> <task_count>
WITH 
task_time AS (
	SELECT 
		ta.task_id,
		ta.activity_id,
		se.provider_conf_id AS conf_id,
		--cost = duration (s) x memory (gb) x computation cost x fixed cost
		to_char(avg(se.duration*0.001*se.memory_size*0.0009765625*0.0000166667 + 0.0000002),'fm999990D9999999999999999') AS task_cost,		
		avg(se.duration)*0.001 AS task_time_duration,
		avg(COALESCE(se.init_duration, 0)*0.001) AS task_time_init_duration,
		avg(se.duration - COALESCE(se.consumed_files_transfer_duration, 0) - COALESCE(se.produced_files_transfer_duration, 0))*0.001 AS task_time_cpu,
		avg(se.consumed_files_transfer_duration)*0.001 AS task_time_read,
		avg(se.produced_files_transfer_duration)*0.001 AS task_time_write,
		count(*) AS task_count
	FROM service_execution se
	JOIN workflow_execution we ON se.we_id = we.we_id
	JOIN vw_service_execution_task st ON se.se_id = st.se_id
	JOIN vw_task ta ON st.task_id = ta.task_id
	WHERE we.we_id in (252,253,254,255,256)
	GROUP BY ta.task_id,
			 ta.activity_id,
			 se.provider_conf_id
	ORDER BY ta.task_id,
			 ta.activity_id,
			 se.provider_conf_id
)
SELECT  t1.task_id,
		t1.activity_id,
		t1.conf_id,
		t1.task_cost,
		t1.task_time_duration,
		t1.task_time_init_duration, 
		t1.task_time_cpu,
		t1.task_time_read,
		t1.task_time_write,
		t1.task_count 
FROM task_time t1
UNION ALL
SELECT  distinct t2.task_id,
		t2.activity_id,
		pc.conf_id AS conf_id, 
		'99999' AS task_cost,
		99999 AS task_time_duration,
		99999 AS task_time_init_duration,
		99999 AS task_time_cpu,
		99999 AS task_time_read,
		99999 AS task_time_write,
		00000 AS task_count
FROM provider_configuration pc 
JOIN provider pr on pc.provider_id = pr.provider_id
CROSS JOIN task_time t2
WHERE pr.provider_tag = 'aws_lambda' AND
	  (t2.task_id, pc.conf_id) NOT IN (SELECT task_id, conf_id FROM task_time)
ORDER BY task_id,
		 activity_id,
		 conf_id;



--->scripts/sql/instance_generator/06_bucket_ranges.sql
--->weids_fx:[252, 253, 254, 255, 256]
--->weids_vm:[267]
--->Generated at 2025-05-30 13:50:46

#<bucket_range_id> <size1_gb> <size2_gb> <cost_per_gb>
SELECT 
    bucket_range_id,
    size1_gb,
    size2_gb,
    cost_per_gb
FROM bucket_ranges
ORDER BY bucket_range_id;




-----------resources/sql/instance_generator/01_totals.sql
-----------'weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437'
-----------Generated at 2025-01-17 14:51:37

#<#tasks> <#config> <#data> <#vms> <#buckets> <#bucket_ranges> <max_running_time> <max_financial_cost>
SELECT 
	(SELECT count(distinct se.task_id) AS _tasks_count
		FROM service_execution se
		WHERE se.workflow_execution_id in ('weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437')
	),
	(SELECT count(configuration_id) AS _configs_count
		FROM provider_configuration pc
	),
	(SELECT count(distinct ef.file_id ) AS _files_count
		FROM service_execution se 
		JOIN execution_file ef ON ef.se_id = se.se_id 
		WHERE se.workflow_execution_id in ('weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437')
	),
	(SELECT 3 AS _vms_count
	),
	(SELECT count(distinct fi.file_bucket ) AS _buckets_count
		FROM service_execution se 
		JOIN execution_file ef ON ef.se_id = se.se_id
		JOIN  file fi ON fi.file_id = ef.file_id
		WHERE se.workflow_execution_id in ('weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437')
	),
	(SELECT 3 AS _bucket_ranges_count
	),
	(SELECT 1000 AS _max_running_time
	),
	(SELECT 999999 AS _max_financial_cost
	);
;

-----------resources/sql/instance_generator/02_task.sql
-----------'weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437'
-----------Generated at 2025-01-17 14:51:37

#<task_id> <activity_id> <task_type__0-VM__1-FX> <vm_cpu_time> <n_input> [<id_input>...] <n_output> [<id_output>...]
SELECT DISTINCT 
	ta.task_id, --se.se_id, se.activity_id,
	ta.activity_id,
	ta.task_type,
	99999 AS vm_cpu_time, --tempo base em vm,
	ta.input_count AS n_input,
	'[' || ta.input_list || ']' AS input_list,
	ta.output_count AS n_output,
	'[' || ta.output_list || ']' AS output_list
FROM service_execution se
JOIN task ta on se.task_id = ta.task_id
WHERE se.workflow_execution_id in ('weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437')
ORDER BY task_id

-----------resources/sql/instance_generator/03_data.sql
-----------'weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437'
-----------Generated at 2025-01-17 14:51:38

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
	WHERE ef.transfer_type = 'produced' AND se.workflow_execution_id in ('weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437')
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
	WHERE ef.transfer_type = 'consumed' AND se.workflow_execution_id in ('weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437')
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

-----------resources/sql/instance_generator/04_vm_cpu.sql
-----------'weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437'
-----------Generated at 2025-01-17 14:51:38

#<vm1_cpu_slowdown> <vm2_cpu_slowdown> <vm3_cpu_slowdown>
SELECT 1 AS vm1_cpu_slowdown, 0.8 AS vm2_cpu_slowdown, 0.75 AS vm3_cpu_slowdown

-----------resources/sql/instance_generator/05_vm_storage.sql
-----------'weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437'
-----------Generated at 2025-01-17 14:51:38

#<vm1_storage> <vm2 _storage> <vm3_storage>
SELECT 10000 AS vm1_storage, 10000 AS vm2_storage, 10000 AS vm3_storage

-----------resources/sql/instance_generator/06_vm_cost.sql
-----------'weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437'
-----------Generated at 2025-01-17 14:51:38

#<vm1_cost> <vm2_cost> <vm3_cost>
SELECT 1 AS vm1_cost, 1.3 AS vm2_cost, 1.5 AS vm3_cost;

-----------resources/sql/instance_generator/07_bandwidth_matrix.sql
-----------'weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437'
-----------Generated at 2025-01-17 14:51:38

#<vm_id> <bandwidth>
SELECT 1 AS vm_id, 1000 AS bandwidth
UNION ALL
SELECT 2 AS vm_id, 1000 AS bandwidth
UNION ALL
SELECT 3 AS vm_id, 1000 AS bandwidth
;

-----------resources/sql/instance_generator/08_time_cost_matrix.sql
-----------'weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437'
-----------Generated at 2025-01-17 14:51:38

#<task_id> <activity_id> <config_id> <task_cost> <task_time_total> <task_time_init> <task_time_cpu> <task_time_read> <task_time_write> <task_count>
WITH 
task_time AS (
	SELECT 
		ta.task_id,
		ta.activity_id,
		se.configuration_id AS config_id,
		--cost = duration (s) x memory (gb) x computation cost x fixed cost
		to_char(avg(se.duration*0.001*se.memory_size*0.0009765625*0.0000166667 + 0.0000002),'fm999990D9999999999999999') AS task_cost,		
		avg(se.duration)*0.001 AS task_time_total,
		avg(COALESCE(se.init_duration, 0)*0.001) AS task_time_init,
		avg(se.duration - COALESCE(se.consumed_files_transfer_duration, 0) - COALESCE(se.produced_files_transfer_duration, 0))*0.001 AS task_time_cpu,
		avg(se.consumed_files_transfer_duration)*0.001 AS task_time_read,
		avg(se.produced_files_transfer_duration)*0.001 AS task_time_write,
		count(*) as task_count
	FROM service_execution se
	JOIN task ta ON se.task_id = ta.task_id
	WHERE se.workflow_execution_id in ('weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437')
	GROUP BY ta.task_id, ta.activity_id, se.configuration_id
	ORDER BY ta.task_id, ta.activity_id, se.configuration_id
)
SELECT  task_id,
		activity_id,
		config_id,
		task_cost,
		task_time_total,
		task_time_init, 
		task_time_cpu,
		task_time_read,
		task_time_write,
		task_count 
FROM task_time t1
UNION ALL
SELECT  distinct t1.task_id,
		t1.activity_id,
		pc.configuration_id AS config_id, 
		'99999' AS task_cost,
		99999 AS task_time_total,
		99999 AS task_time_init,
		99999 AS task_time_cpu,
		99999 AS task_time_read,
		99999 AS task_time_write,
		00000 AS task_count
FROM provider_configuration pc, task_time t1
WHERE (t1.task_id, pc.configuration_id) NOT IN (SELECT task_id, config_id FROM task_time)
ORDER BY task_id, activity_id, config_id;

-----------resources/sql/instance_generator/10_bucket_ranges.sql
-----------'weid_1735311414938','weid_1735318446694','weid_1735319031426','weid_1735319100179','weid_1735319150437'
-----------Generated at 2025-01-17 14:51:38

#<bucket_range_id> <size1_gb> <size2_gb> <cost_per_gb>
SELECT 1 AS bucket_range_id, 0 AS size1_gb, 50*1024 AS size2_gb, 0.0405 AS cost_per_gb
UNION ALL
SELECT 2 AS bucket_range_id, 50*1024 AS size1_gb, 450*1024 AS size2_gb, 0.039 AS cost_per_gb
UNION ALL
SELECT 3 AS bucket_range_id, 450*1024 AS size1_gb, 99999999999999 AS size2_gb, 0.037 AS cost_per_gb



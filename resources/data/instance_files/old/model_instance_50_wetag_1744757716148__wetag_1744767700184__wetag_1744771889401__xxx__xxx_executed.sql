-----------scripts/sql/instance_generator/01_totals.sql
-----------'wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx'
-----------Generated at 2025-04-16 11:46:23

#<#tasks> <#config> <#data> <#vms> <#buckets> <#bucket_ranges> <max_running_time> <max_financial_cost>
SELECT 
	(SELECT count(distinct st.task_id) AS _tasks_count
		FROM service_execution se
		JOIN workflow_execution we ON se.we_id = we.we_id
		JOIN vw_service_execution_task st ON se.se_id = st.se_id
		WHERE we.execution_tag in ('wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx')
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
		WHERE we.execution_tag in ('wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx')
	),
	(SELECT count(*) AS _vms_count
		FROM vm_configurations
	),
	(SELECT count(distinct fi.file_bucket ) AS _buckets_count
		FROM service_execution se
		JOIN workflow_execution we ON se.we_id = we.we_id
		JOIN execution_file ef ON ef.se_id = se.se_id
		JOIN file fi ON fi.file_id = ef.file_id
		WHERE we.execution_tag in ('wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx')
	),
	(SELECT count(*) AS _bucket_ranges_count
		FROM bucket_ranges
	),
	(SELECT 1000 AS _max_running_time
	),
	(SELECT 999999 AS _max_financial_cost
	);
;

-----------scripts/sql/instance_generator/02_task.sql
-----------'wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx'
-----------Generated at 2025-04-16 11:46:32

#<task_id> <activity_id> <task_type__0-VM__1-VM_FX> <vm_cpu_time> <n_input> [<id_input>...] <n_output> [<id_output>...]
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
WHERE we.execution_tag in ('wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx')
ORDER BY ta.activity_id, ta.task_id

-----------scripts/sql/instance_generator/03_data.sql
-----------'wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx'
-----------Generated at 2025-04-16 11:46:32

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
	WHERE ef.transfer_type = 'produced' AND we.execution_tag in ('wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx')
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
	WHERE ef.transfer_type = 'consumed' AND we.execution_tag in ('wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx')
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

-----------scripts/sql/instance_generator/04_vm_cpu.sql
-----------'wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx'
-----------Generated at 2025-04-16 11:46:32

#<vm1_cpu_slowdown> <vm2_cpu_slowdown> ... <vm10_cpu_slowdown>
SELECT 
    MAX(CASE WHEN vm_id = 1 THEN cpu_slowdown END) AS vm1_cpu_slowdown,
    MAX(CASE WHEN vm_id = 2 THEN cpu_slowdown END) AS vm2_cpu_slowdown,
    MAX(CASE WHEN vm_id = 3 THEN cpu_slowdown END) AS vm3_cpu_slowdown,
    MAX(CASE WHEN vm_id = 4 THEN cpu_slowdown END) AS vm4_cpu_slowdown,
    MAX(CASE WHEN vm_id = 5 THEN cpu_slowdown END) AS vm5_cpu_slowdown,
    MAX(CASE WHEN vm_id = 6 THEN cpu_slowdown END) AS vm6_cpu_slowdown,
    MAX(CASE WHEN vm_id = 7 THEN cpu_slowdown END) AS vm7_cpu_slowdown,
    MAX(CASE WHEN vm_id = 8 THEN cpu_slowdown END) AS vm8_cpu_slowdown,
    MAX(CASE WHEN vm_id = 9 THEN cpu_slowdown END) AS vm9_cpu_slowdown
FROM vm_configurations;

-----------scripts/sql/instance_generator/05_vm_storage.sql
-----------'wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx'
-----------Generated at 2025-04-16 11:46:33

#<vm1_storage> <vm2 _storage> <vm3_storage>
SELECT 
    MAX(CASE WHEN vm_id = 1 THEN storage END) AS vm1_storage,
    MAX(CASE WHEN vm_id = 2 THEN storage END) AS vm2_storage,
    MAX(CASE WHEN vm_id = 3 THEN storage END) AS vm3_storage--,
    -- MAX(CASE WHEN vm_id = 4 THEN storage END) AS vm4_storage,
    -- MAX(CASE WHEN vm_id = 5 THEN storage END) AS vm5_storage,
    -- MAX(CASE WHEN vm_id = 6 THEN storage END) AS vm6_storage,
    -- MAX(CASE WHEN vm_id = 7 THEN storage END) AS vm7_storage,
    -- MAX(CASE WHEN vm_id = 8 THEN storage END) AS vm8_storage,
    -- MAX(CASE WHEN vm_id = 9 THEN storage END) AS vm9_storage
FROM vm_configurations;

-----------scripts/sql/instance_generator/06_vm_cost.sql
-----------'wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx'
-----------Generated at 2025-04-16 11:46:33

#<vm1_cost> <vm2_cost> <vm3_cost>
SELECT 
    MAX(CASE WHEN vm_id = 1 THEN cost END) AS vm1_cost,
    MAX(CASE WHEN vm_id = 2 THEN cost END) AS vm2_cost,
    MAX(CASE WHEN vm_id = 3 THEN cost END) AS vm3_cost--,
    -- MAX(CASE WHEN vm_id = 4 THEN cost END) AS vm4_cost,
    -- MAX(CASE WHEN vm_id = 5 THEN cost END) AS vm5_cost,
    -- MAX(CASE WHEN vm_id = 6 THEN cost END) AS vm6_cost,
    -- MAX(CASE WHEN vm_id = 7 THEN cost END) AS vm7_cost,
    -- MAX(CASE WHEN vm_id = 8 THEN cost END) AS vm8_cost,
    -- MAX(CASE WHEN vm_id = 9 THEN cost END) AS vm9_cost
FROM vm_configurations;

-----------scripts/sql/instance_generator/07_bandwidth_matrix.sql
-----------'wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx'
-----------Generated at 2025-04-16 11:46:33

#<vm_id> <bandwidth>
SELECT vm_id, bandwidth FROM vm_configurations;

-----------scripts/sql/instance_generator/08_time_cost_matrix.sql
-----------'wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx'
-----------Generated at 2025-04-16 12:16:56

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
	WHERE we.execution_tag in ('wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx', 'wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx')
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

-----------scripts/sql/instance_generator/10_bucket_ranges.sql
-----------'wetag_1744757716148','wetag_1744767700184','wetag_1744771889401','xxx','xxx'
-----------Generated at 2025-04-16 12:16:56

#<bucket_range_id> <size1_gb> <size2_gb> <cost_per_gb>
SELECT 
    bucket_range_id,
    size1_gb,
    size2_gb,
    cost_per_gb
FROM bucket_ranges;


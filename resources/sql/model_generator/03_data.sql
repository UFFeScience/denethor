--# <data_id> <data_size> <read_time_avg> <write_time_avg> <is_static 0-dinamic 1-static> <n_source_devices - 0 se for dinamico> [<device_id> ... ]
WITH 
produced_file AS (
	SELECT
		ef.file_id AS produced_file_id,
		CAST(avg(f.file_size) AS INTEGER) AS produced_file_size,
		avg(ef.transfer_duration)*0.001 AS write_time_avg
	FROM execution_file ef
	JOIN file f ON f.file_id = ef.file_id
	JOIN service_execution se ON se.se_id = ef.se_id
	WHERE ef.transfer_type = 'produced' AND se.workflow_execution_id in ('weid', 'weid_1724184708846')
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
	WHERE ef.transfer_type = 'consumed' AND se.workflow_execution_id in ('weid', 'weid_1724184708846')
	GROUP BY ef.file_id
)
SELECT 
	COALESCE(consumed_file_id, produced_file_id) AS data_id,
	COALESCE(consumed_file_size, produced_file_size) AS data_size,
	read_time_avg,
	write_time_avg,
	-- CASE 
	-- 	WHEN produced_file_id IS NOT NULL THEN 'dynamic'
	-- 	WHEN produced_file_id IS NULL AND consumed_file_id IS NOT NULL THEN 'static'
	-- 	ELSE 'error'
	-- END AS data_type,
	CASE 
		WHEN produced_file_id IS NOT NULL THEN 0
		WHEN produced_file_id IS NULL AND consumed_file_id IS NOT NULL THEN 1
		ELSE -1
	END AS is_static,
	CASE 
		WHEN produced_file_id IS NOT NULL THEN 0
		WHEN produced_file_id IS NULL AND consumed_file_id IS NOT NULL THEN 1
		ELSE -1
	END AS n_source_devices,
	'[denethor_bucket]' AS device_list
FROM consumed_files 
FULL OUTER JOIN  produced_file ON produced_file_id = consumed_file_id	
ORDER BY consumed_file_id;
-- select * from consumed_files
-- full outer join  produced_file on produced_file_id = consumed_file_id	
-- order by consumed_file_id;
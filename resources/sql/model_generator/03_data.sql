--DATA
--<data_id> <size> <read_time_avg> <write_time_avg> <is_static 0-dinamic 1-static> <n_source_devices - 0 se for dinamico> [<device_id> ... ]
SELECT 
		f.file_id AS data_id,
	CAST(f.file_size AS INTEGER) AS file_size,
	CASE
		WHEN ft.file_type = 'dynamic' THEN 0
		WHEN ft.file_type = 'static' THEN 1
	END AS is_static,
	CASE
		WHEN ft.file_type = 'dynamic' THEN 0
		WHEN ft.file_type = 'static' THEN 1
	END AS n_source_devices,
	'[denethor_bucket]' AS device_list
FROM file f
JOIN vw_file_type ft ON f.file_id = ft.file_id
WHERE ft.workflow_execution_id in ('weid', 'weid_1724184708846')
ORDER BY is_static DESC, f.file_id;





--TESTE NOVO SQL

--DATA
--<data_id> <size> <read_time_avg> <write_time_avg> <is_static 0-dinamic 1-static> <n_source_devices - 0 se for dinamico> [<device_id> ... ]
WITH file_type AS (
	SELECT distinct
		ef.se_id, 
		ef.file_id, 
		'dynamic' AS file_type,
		0 AS is_static,
		0 AS n_source_devices
	FROM execution_file ef
	WHERE ef.transfer_type = 'produced' OR EXISTS (select 1 FROM execution_file ef2 where ef2.file_id = ef.file_id and ef2.transfer_type = 'consumed')
	UNION
	SELECT distinct
		ef.se_id, 
		ef.file_id, 
		'static' AS file_type,
		1 AS is_static,
		1 AS n_source_devices
	FROM execution_file ef
	WHERE ef.transfer_type = 'consumed'
	AND ef.file_id NOT IN (
		SELECT ef2.file_id
		FROM execution_file ef2
		WHERE ef2.transfer_type = 'produced'
	)
)
SELECT
	ef.file_id AS data_id,
	CAST(f.file_size AS INTEGER) AS file_size,
	ef.transfer_duration,
	ef.transfer_type,
	ft.file_type,
	ft.is_static,
	ft.n_source_devices,
	'[denethor_bucket]' AS device_list
FROM service_execution se
JOIN execution_file ef ON ef.se_id = se.se_id
JOIN file f on f.file_id = ef.file_id
left OUTER JOIN file_type ft on ft.se_id = se.se_id and ft.file_id = ef.file_id
WHERE se.workflow_execution_id in ('weid', 'weid_17241847088461', 'weid_1724428668735')
order by ef.file_id;


ORDER BY f.file_id;



SELECT 
		f.file_id AS data_id,
	CAST(f.file_size AS INTEGER) AS file_size,
	CASE
		WHEN ft.file_type = 'dynamic' THEN 0
		WHEN ft.file_type = 'static' THEN 1
	END AS is_static,
	CASE
		WHEN ft.file_type = 'dynamic' THEN 0
		WHEN ft.file_type = 'static' THEN 1
	END AS n_source_devices,
	
FROM file f
JOIN vw_file_type ft ON f.file_id = ft.file_id
WHERE ft.workflow_execution_id in ('weid', 'weid_1724428668735')
ORDER BY f.file_id;







select * from vw_file_type;
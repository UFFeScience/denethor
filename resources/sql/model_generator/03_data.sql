--DATA
--<data_id> <size> <is_static 0-dinamic 1-static> <n_source_devices - 0 se for dinamico> [<device_id> ... ]         
SELECT 
		f.file_id AS data_id,
	CAST(f.file_size AS INTEGER) AS file_size,
	CASE
		WHEN ft.file_type = 'static' THEN 1
		WHEN ft.file_type = 'dynamic' THEN 0
	END AS is_static,
	CASE
		WHEN ft.file_type = 'static' THEN 1
		WHEN ft.file_type = 'dynamic' THEN 0
	END AS n_source_devices,
	'[denethor_bucket]' AS device_list
FROM file f
JOIN vw_file_type ft ON f.file_id = ft.file_id
WHERE ft.workflow_execution_id in ('weid', 'weid_1724184708846')
ORDER BY is_static DESC, f.file_id;
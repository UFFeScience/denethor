--#<#tasks> <#config> <#data> <#vms> <#buckets> <#bucket_ranges> <max_running_time> <max_financial_cost>
SELECT 
	(SELECT count(distinct se.task_id) AS _tasks_count
		FROM service_execution se
		WHERE se.workflow_execution_id in ('[weid]')
	),
	(SELECT count(configuration_id) AS _configs_count
		FROM provider_configuration pc
	),
	(SELECT count(distinct ef.file_id ) AS _files_count
		FROM service_execution se 
		JOIN execution_file ef ON ef.se_id = se.se_id 
		WHERE se.workflow_execution_id in ('[weid]')
	),
	(SELECT 3 AS _vms_count
	),
	(SELECT count(distinct fi.file_bucket ) AS _buckets_count
		FROM service_execution se 
		JOIN execution_file ef ON ef.se_id = se.se_id
		JOIN  file fi ON fi.file_id = ef.file_id
		WHERE se.workflow_execution_id in ('[weid]')
	),
	(SELECT 3 AS _bucket_ranges_count
	),
	(SELECT 1000 AS _max_running_time
	),
	(SELECT 999999 AS _max_financial_cost
	);
;
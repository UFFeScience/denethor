--# <#tasks> <#config> <#data> <#devices_vms> <#buckets> <#ranges> <max_running_time> <max_financial_cost>
SELECT 
	(SELECT count(distinct se.task_id) AS _tasks
		FROM service_execution se
		WHERE se.workflow_execution_id in ('weid_1724184708846')
	),
	(SELECT count(distinct configuration_id) AS _configs
		FROM service_execution se
		WHERE se.workflow_execution_id in ('weid_1724184708846')
	),
	(SELECT count(distinct ef.file_id ) AS _files
		FROM service_execution se 
		JOIN execution_file ef ON ef.se_id = se.se_id 
		WHERE se.workflow_execution_id in ('weid_1724184708846')
	),
	(SELECT 3 AS _devices_vms
	),
	(SELECT count(distinct fi.file_bucket ) AS _buckets
		FROM service_execution se 
		JOIN execution_file ef ON ef.se_id = se.se_id
		JOIN  file fi ON fi.file_id = ef.file_id
		WHERE se.workflow_execution_id in ('weid_1724184708846')
	),
	(SELECT 3 AS _bucket_ranges
	),
	(SELECT 1000 AS _max_running_time
	),
	(SELECT 999999 AS _max_financial_cost
	);
;
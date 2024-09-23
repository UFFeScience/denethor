--TIME FUNCTION MATRIX (task/config)
--<task_id> <config_id> <task_time_total> <task_time_cpu> <task_time_read> <task_time_write>
SELECT 
	ta.task_id,
	configuration_id AS config_id,
	se.duration*0.001 AS task_time_total,
	(se.duration - COALESCE(se.consumed_files_transfer_duration, 0) - COALESCE(se.produced_files_transfer_duration, 0))*0.001 AS task_time_cpu,
	COALESCE(se.consumed_files_transfer_duration, 0)*0.001 AS task_time_read,
	COALESCE(se.produced_files_transfer_duration, 0)*0.001 AS task_time_write
FROM service_execution se
JOIN task ta ON se.task_id = ta.task_id
WHERE se.workflow_execution_id in ('weid', 'weid_1724184708846')
ORDER BY task_id;
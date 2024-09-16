--TIME FUNCTION MATRIX (task/config)
--<task_id> <config_id> <task_time>...
SELECT 
	ta.task_id,
	configuration_id AS config_id,
	se.duration*0.001 AS task_time_s
FROM service_execution se
JOIN task ta ON se.task_id = ta.task_id
WHERE se.workflow_execution_id in ('weid', 'weid_1724184708846')
ORDER BY task_id;
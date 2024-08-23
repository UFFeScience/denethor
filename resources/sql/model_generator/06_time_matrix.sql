--TIME FUNCTION MATRIX (task/config) (obter a partir das execuções na aws)
--<task_id> <config_id> <task_time>...
--1 1 12
--2 1 23
SELECT 
	se.se_id AS task_id,
	configuration_id AS config_id,
	se.duration AS task_time_ms
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
WHERE se.workflow_execution_id = 'weid_1724184708846'
ORDER BY task_id;
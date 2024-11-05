--#<task_id> <activity_id> <config_id> <task_time_total> <task_time_init> <task_time_cpu> <task_time_read> <task_time_write> <task_count>
WITH 
task_time AS (
	SELECT 
		ta.task_id,
		ta.activity_id,
		se.configuration_id AS config_id,
		avg(se.duration)*0.001 AS task_time_total,
		avg(COALESCE(se.init_duration, 0)*0.001) AS task_time_init,
		avg(se.duration - COALESCE(se.consumed_files_transfer_duration, 0) - COALESCE(se.produced_files_transfer_duration, 0))*0.001 AS task_time_cpu,
		avg(se.consumed_files_transfer_duration)*0.001 AS task_time_read,
		avg(se.produced_files_transfer_duration)*0.001 AS task_time_write,
		count(*) as task_count
	FROM service_execution se
	JOIN task ta ON se.task_id = ta.task_id
	WHERE se.workflow_execution_id in ('[weid]')
	GROUP BY ta.task_id, ta.activity_id, se.configuration_id
	ORDER BY ta.task_id, ta.activity_id, se.configuration_id
)
SELECT  task_id,
		activity_id,
		config_id,
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
		99999 AS task_time_total,
		99999 AS task_time_init,
		99999 AS task_time_cpu,
		99999 AS task_time_read,
		99999 AS task_time_write,
		00000 AS task_count
FROM provider_configuration pc, task_time t1
WHERE (t1.task_id, pc.configuration_id) NOT IN (
		SELECT task_id, config_id FROM task_time)
ORDER BY task_id, activity_id, config_id;
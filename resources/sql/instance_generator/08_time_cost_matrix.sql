--#<task_id> <activity_id> <conf_id> <task_cost> <task_time_duration> <task_time_init> <task_time_cpu> <task_time_read> <task_time_write> <task_count>
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
	WHERE we.execution_tag in ('[wetag]', 'wetag_1743638228939')
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
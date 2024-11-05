--#<task_id> <activity_id> <config_id> <task_cost> <task_count>
WITH task_cost AS (
	SELECT 
		ta.task_id,
		ta.activity_id,
		se.configuration_id AS config_id,
		--cost = duration (s) x memory (gb) x computation cost x fixed cost
		to_char(avg(se.duration*0.001*se.memory_size*0.0009765625*0.0000166667 + 0.0000002),'fm999990D9999999999999999') AS task_cost,
		count(*) as task_count
	FROM service_execution se
	JOIN task ta ON ta.task_id = se.task_id
	WHERE se.workflow_execution_id in ('[weid]')
	GROUP BY ta.task_id, ta.activity_id, se.configuration_id
	ORDER BY ta.task_id, ta.activity_id, se.configuration_id
)
SELECT  task_id,
		activity_id,
		config_id,
		task_cost,
		task_count 
FROM task_cost t1
UNION ALL
SELECT  distinct t1.task_id,
		t1.activity_id,
		pc.configuration_id AS config_id, 
		'99999' AS task_cost,
		00000 AS task_count
FROM provider_configuration pc, task_cost t1
WHERE (t1.task_id, pc.configuration_id) NOT IN (
		SELECT task_id, config_id FROM task_cost)
ORDER BY task_id, activity_id, config_id;
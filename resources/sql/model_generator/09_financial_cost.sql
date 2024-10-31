--#<task_id> <config_id> <task_cost>
SELECT 
	ta.task_id,
	se.configuration_id AS config_id,
	-- cost = duration (s) x memory (gb) x computation cost x fixed cost
	to_char(se.duration*0.001*se.memory_size*0.0009765625*0.0000166667 + 0.0000002,'fm999990D9999999999999999999999') AS task_cost
FROM service_execution se
JOIN task ta ON ta.task_id = se.task_id
WHERE se.workflow_execution_id in ('weid', 'weid_1724184708846')
ORDER BY task_id;
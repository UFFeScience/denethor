--FINANCIAL COST FUNCTION MATRIX (task/config)
--<task_id> <config_id>  <cost>
--1 1 1.23
SELECT 
	se.se_id AS task_id,
	configuration_id AS config_id,
	-- duração (s) x memória (gb) x custo unitário da computação  +  custo fixo por solicitação
	to_char(se.duration*0.001*128*0.0009765625*0.0000166667 + 0.0000002,'fm999990D9999999999999999999999') AS task_cost
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
WHERE se.workflow_execution_id = 'weid_1724184708846'
ORDER BY task_id;
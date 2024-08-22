SELECT * FROM vw_service_execution_info_last;

--Totais
--<#tasks> <#config> <#data> <#devices> <#periods> <#buckets> <#ranges> <max_financial_cost>
SELECT 
	(SELECT count(*) AS _tasks FROM service_execution se where se.workflow_execution_id = 'weid_1724184708846'),
	(SELECT count(*) AS _config FROM provider_configuration),
	(SELECT count(*) AS _data FROM file),
	(SELECT 3 AS _devices),
	(SELECT 1 AS _periods),
	(SELECT 1 AS _buckets),
	(SELECT 2 AS _ranges),
	(SELECT 100000 AS _max_financial_cost)


--Tarefas, tipos, configuração, cpu, input (total e lista), output (total e lista)
--<task_id> <task_type 0-VM 1-FX> <config_id. -1 se tipo for VM> <cpu_time> <n_input> [<id_input> .. ] < n_output  > [<id_output> .. ] 
SELECT 
	se.se_id AS task_id,
	1 AS task_type__0vm__1fx,
	configuration_id,
	1 AS cpu_time, --tempo base
	(SELECT count(*) 
		FROM file fi
		JOIN execution_file ef ON ef.file_id = fi.file_id and ef.se_id = se.se_id
		WHERE ef.transfer_type = 'consumed') AS n_input,
	(SELECT STRING_AGG(fi.file_name, ', ') 
		FROM file fi
		JOIN execution_file ef ON ef.file_id = fi.file_id and ef.se_id = se.se_id
		WHERE ef.transfer_type = 'consumed') AS input_list,
	(SELECT count(*) 
		FROM file fi
		JOIN execution_file ef ON ef.file_id = fi.file_id and ef.se_id = se.se_id
		WHERE ef.transfer_type = 'produced') AS n_output,
	(SELECT STRING_AGG(fi.file_name, ', ') 
		FROM file fi
		JOIN execution_file ef ON ef.file_id = fi.file_id and ef.se_id = se.se_id
		WHERE ef.transfer_type = 'produced') AS output_list
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
WHERE se.workflow_execution_id = 'weid_1724184708846'
ORDER BY task_id;



--<data_id> <size> <is_static 0-dynamic 1-static> <n_source_devices - 0 se for dinamico> [<device_id> ... ]         
SELECT f.file_name AS data_id,
		f.file_size AS file_size,
		CASE
			WHEN ft.file_type = 'static' THEN 1
			WHEN ft.file_type = 'dynamic' THEN 0
		END AS is_static,
		CASE
			WHEN ft.file_type = 'static' THEN 1
			WHEN ft.file_type = 'dynamic' THEN 0
		END AS n_source_devices,
		'denethor_bucket' AS device_list
FROM file f
JOIN vw_file_type ft ON f.file_id = ft.file_id
WHERE ft.workflow_execution_id = 'weid_1724184708846'
order by is_static desc, f.file_id;

--<vm1_cpu_slowdown> <vm2_cpu_slowdown> ... <vm*_cpu_slowdown>
--<vm1_storage> <vm2_storage> ... <vm* _storage>
--<vm1_cost> <vm2_cost> ... <vm*_cost>
SELECT 1 AS vm1_cpu_slowdown, 0.8 AS vm2_cpu_slowdown, 0.75 AS vm3_cpu_slowdown
union all
SELECT 10000 AS vm1_storage, 10000 AS vm2_storage, 10000 AS vm3_storage
union all
SELECT 1 AS vm1_cost, 1.3 AS vm2_cost, 1.5 AS vm3_cost;

--BANDWIDTH MATRIX (estático)
--<vm_id> <bandwidth>
SELECT 1 AS vm_id, 1000 AS bandwidth
union all
SELECT 2 AS vm_id, 1000 AS bandwidth
union all
SELECT 3 AS vm_id, 1000 AS bandwidth
;

--TIME FUNCTION MATRIX (task/config) (obter a partir das execuções na aws)
--<task_id> <config_id> <task_time>...
--1 1 12
--2 1 23
SELECT se.se_id task_id,
		CASE 
			WHEN se.activity_id = 1 THEN 1
			WHEN se.activity_id = 2 THEN 2
			WHEN se.activity_id = 3 THEN 3
			WHEN se.activity_id = 4 THEN 1
		END AS config_id,
		se.duration AS task_time_ms
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
WHERE se.workflow_execution_id = 'weid_1724184708846'
ORDER BY task_id



--FINANCIAL COST FUNCTION MATRIX (task/config)
--<task_id> <config_id>  <cost>
--1 1 1.23
SELECT se.se_id task_id,
		CASE 
			WHEN se.activity_id = 1 THEN 1
			WHEN se.activity_id = 2 THEN 2
			WHEN se.activity_id = 3 THEN 3
			WHEN se.activity_id = 4 THEN 1
		END AS config_id,
		-- duração (s) x memória (gb) x custo unitário da computação  +  custo fixo por solicitação
		to_char(se.duration*0.001*128*0.0009765625*0.0000166667 + 0.0000002,'fm999990D9999999999999999999999') AS task_cost
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
WHERE se.workflow_execution_id = 'weid_1724184708846'
ORDER BY task_id;


-- BUCKET RANGE LIST
-- <range_id> <size1> <size2> <cost>
-- [range1 0 100 0.15 ]
-- [range2 100 500 0.138]
SELECT 1 AS range_id, 0 AS size1_tb, 50 AS size2_tb, 0.0405 AS cost_per_gb
union all
SELECT 2 AS range_id, 50 AS size1_tb, 450 AS size2_tb, 0.039 AS cost_per_gb
union all
SELECT 3 AS range_id, 450 AS size1_tb, 999999999999 AS size2_tb, 0.037 AS cost_per_gb

SELECT * FROM provider_configuration;
SELECT * FROM workflow_activity;


--grafico com tempos de cada tarefa para cada atividade
-- csv do service_exec
-- concluir o arquivo
-- rodar em VM

-- task é o service_exec!
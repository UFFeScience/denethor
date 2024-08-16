--Totais
--<#tasks> <#config> <#data> <#devices> <#periods> <#buckets> <#ranges> <max_financial_cost>
select 
	(select count(*) as _tasks from service_execution),
	(select count(*) as _config from provider_configuration),
	(select count(*) as _data from file),
	(select 3 as _devices),
	(select 1 as _periods),
	(select 1 as _buckets),
	(select 2 as _ranges),
	(select 100000 as _max_financial_cost)


--Tarefas, tipos, configuração, cpu, input (total e lista), output (total e lista)
--<task_id> <task_type 0-VM 1-FX> <config_id. -1 se tipo for VM> <cpu_time> <n_input> [<id_input> .. ] < n_output  > [<id_output> .. ] 
select se.se_id as task_id,
		1 as task_type__0vm__1fx,
		case 
			when wa.activity_id = 1 then 1
			when wa.activity_id = 2 then 2
			when wa.activity_id = 3 then 3
			when wa.activity_id = 4 then 1
		end as config_id,
		1 as cpu_time, --tempo base
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
ORDER BY task_id;



--<data_id> <size> <is_static 0-dynamic 1-static> <n_source_devices - 0 se for dinamico> [<device_id> ... ]         
select f.file_name as data_id,
		f.file_size as size,
		case
			when ft.file_type = 'static' then 1
			when ft.file_type = 'dynamic' then 0
		end as is_static,
		case
			when ft.file_type = 'static' then 1
			when ft.file_type = 'dynamic' then 0
		end as n_source_devices,
		'denethor_bucket' as device_list
from file f
join vw_file_type ft on f.file_id = ft.file_id
order by is_static desc, f.file_name;

--<vm1_cpu_slowdown> <vm2_cpu_slowdown> ... <vm*_cpu_slowdown>
--<vm1_storage> <vm2_storage> ... <vm* _storage>
--<vm1_cost> <vm2_cost> ... <vm*_cost>
select 1 as vm1_cpu_slowdown, 0.8 as vm2_cpu_slowdown, 0.75 as vm3_cpu_slowdown
union all
select 10000 as vm1_storage, 10000 as vm2_storage, 10000 as vm3_storage
union all
select 1 as vm1_cost, 1.3 as vm2_cost, 1.5 as vm3_cost;

--BANDWIDTH MATRIX (estático)
--<vm_id> <bandwidth>
select 1 as vm_id, 1000 as bandwidth
union all
select 2 as vm_id, 1000 as bandwidth
union all
select 3 as vm_id, 1000 as bandwidth
;

--TIME FUNCTION MATRIX (task/config) (obter a partir das execuções na aws)
--<task_id> <config_id> <task_time>...
--1 1 12
--2 1 23
SELECT se.se_id task_id,
		case 
			when se.activity_id = 1 then 1
			when se.activity_id = 2 then 2
			when se.activity_id = 3 then 3
			when se.activity_id = 4 then 1
		end as config_id,
		se.duration AS task_time_ms
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
ORDER BY task_id



--FINANCIAL COST FUNCTION MATRIX (task/config) (multiplicar o tempo x custo??)
--<task_id> <config_id>  <cost>
--1 1 1.23
SELECT se.se_id task_id,
		case 
			when se.activity_id = 1 then 1
			when se.activity_id = 2 then 2
			when se.activity_id = 3 then 3
			when se.activity_id = 4 then 1
		end as config_id,
		se.duration*0.0002 AS task_cost
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
ORDER BY task_id;


-- BUCKET RANGE LIST
-- <range_id> <size1> <size2> <cost>
-- [range1 0 100 0.15 ]
-- [range2 100 500 0.138]
select 1 as range_id, 0 as size1, 10000 as size2, 10 as cost
union all
select 2 as range_id, 10000 as size1, 100000 as size2, 15 as cost

select * from provider_configuration;
select * from workflow_activity;


--grafico com tempos de cada tarefa para cada atividade
-- csv do service_exec
-- concluir o arquivo
-- rodar em VM

-- task é o service_exec!
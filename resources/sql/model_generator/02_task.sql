--Tarefas, tipos, configuração, cpu, input (total e lista), output (total e lista)
--<task_id> <task_type 0-VM 1-FX> <config_id. -1 se tipo for VM> <cpu_time> <n_input> [<id_input> .. ] < n_output  > [<id_output> .. ] 
SELECT 
	se.se_id AS task_id,
	1 AS task_type__0vm__1fx,
	configuration_id AS config_id,
	1 AS cpu_time, --tempo base
	(SELECT count(*) -- sem virgulas na lista de arquivos
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
WHERE se.workflow_execution_id = '[weid]'
ORDER BY task_id;
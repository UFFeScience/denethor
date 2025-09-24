--#<#tasks> <#config> <#data> <#vms> <#buckets> <#bucket_ranges> <max_running_time_ms> <max_financial_cost>
SELECT 
	(SELECT count(distinct st.task_id) AS _tasks_count
		FROM service_execution se
		JOIN workflow_execution we ON se.we_id = we.we_id
		JOIN vw_service_execution_task st ON se.se_id = st.se_id
		WHERE we.[we_column] in ([we_values])
	),
	(SELECT count(pc.conf_id) AS _configs_count
		FROM provider_configuration pc
		JOIN provider pr on pc.provider_id = pr.provider_id
		WHERE pr.provider_tag = 'aws_lambda'
	),
	(SELECT count(distinct ef.file_id ) AS _files_count
		FROM service_execution se
		JOIN workflow_execution we ON se.we_id = we.we_id 
		JOIN execution_file ef ON ef.se_id = se.se_id 
		WHERE we.[we_column] in ([we_values])
	),
	(SELECT count(*) AS _vms_count
		FROM vm_configurations
	),
	(SELECT count(distinct fi.file_bucket ) AS _buckets_count
		FROM service_execution se
		JOIN workflow_execution we ON se.we_id = we.we_id
		JOIN execution_file ef ON ef.se_id = se.se_id
		JOIN file fi ON fi.file_id = ef.file_id
		WHERE we.[we_column] in ([we_values])
	),
	(SELECT count(*) AS _bucket_ranges_count
		FROM bucket_ranges
	),
	(SELECT max(t.max_workflow_duration_ms) AS _max_running_time_ms
		FROM (
			SELECT 
				we.we_id,
				se.provider_conf_id,
				sum(se.duration) AS max_workflow_duration_ms,
				count(*) AS task_count
			FROM service_execution se
			JOIN workflow_execution we ON se.we_id = we.we_id
			WHERE we.[we_column] in ([we_values])
			GROUP BY we.we_id, se.provider_conf_id
			ORDER BY we.we_id
		) t
	),
	(SELECT max(t.max_workflow_cost) AS _max_financial_cost
		FROM (
			SELECT 
				we.we_id,
				se.provider_conf_id,
				--cost = duration (s) x memory (gb) x computation cost x fixed cost
				to_char(sum(se.duration*0.001*se.memory_size*0.0009765625*0.0000166667 + 0.0000002),'fm999990D9999999999999999') AS max_workflow_cost,		
				count(*) AS task_count
			FROM service_execution se
			JOIN workflow_execution we ON se.we_id = we.we_id
			WHERE we.[we_column] in ([we_values])
			GROUP BY we.we_id, se.provider_conf_id
			ORDER BY we.we_id
		) t
	);
;
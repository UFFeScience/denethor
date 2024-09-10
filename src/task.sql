SELECT 
		row_number() over() as task_id,
		se.activity_id,
		count(*) as total,
		(SELECT STRING_AGG(to_char(file_id, 'fm99999999'), ', ') 
		FROM 
			( select fi.file_id from file fi
				JOIN execution_file ef ON ef.file_id = fi.file_id and ef.se_id = se.se_id
				WHERE ef.transfer_type = 'consumed'
				order by fi.file_id
				)
		) AS input_id_list
    FROM 
        service_execution se
	JOIN workflow_activity wa ON wa.activity_id = se.activity_id
	group by se.activity_id, input_id_list
	order by task_id, se.activity_id, total
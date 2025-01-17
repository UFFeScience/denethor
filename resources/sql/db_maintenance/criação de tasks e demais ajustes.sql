--criando e inserindo tarefas a partir das execuções
with service_execution_with_input_output_list as ( 
	SELECT 
		se.activity_id,
		se.se_id,
		(SELECT COALESCE(MIN(ef.file_id),0) 
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'consumed'
		) AS first_input_id,
		(SELECT COALESCE(MIN(ef.file_id),0) 
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'produced'
		) AS first_output_id,
		(SELECT count(*)
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'consumed'
		) AS input_count,
		(SELECT count(*) 
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'produced'
		) AS output_count,
		(SELECT COALESCE(STRING_AGG(ef.file_id::VARCHAR, ',' ORDER BY ef.file_id), 'None')
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'consumed'
		) AS  input_list,
		(SELECT COALESCE(STRING_AGG(ef.file_id::VARCHAR, ',' ORDER BY ef.file_id), 'None')  
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'produced'
		) AS output_list
	FROM service_execution se
	GROUP BY se.se_id ,se.activity_id
	ORDER BY se_id, activity_id, first_input_id
)
insert into task(activity_id, input_count, input_list, output_count, output_list)
select 	activity_id, input_count, input_list, output_count, output_list from (
	SELECT DISTINCT
			t1.activity_id,
			t1.first_input_id,
			t1.first_output_id,
			t1.input_count,
			t1.output_count,
			t1.input_list,
			t1.output_list
	FROM service_execution_with_input_output_list t1
	WHERE NOT EXISTS (select 1 from task ta 
						where t1.activity_id = ta.activity_id and
							  t1.input_list  = ta.input_list and
							  t1.output_list = ta.output_list)
	ORDER BY activity_id, first_input_id
);


select * from task order by task_id desc;


--update de service execution com os novos task_id
with service_execution_with_input_output_list as ( 
	SELECT 
		se.activity_id,
		se.se_id,
		(SELECT COALESCE(MIN(ef.file_id),0) 
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'consumed'
		) AS first_input_id,
		(SELECT COALESCE(MIN(ef.file_id),0) 
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'produced'
		) AS first_output_id,
		(SELECT count(*)
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'consumed'
		) AS input_count,
		(SELECT count(*) 
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'produced'
		) AS output_count,
		(SELECT COALESCE(STRING_AGG(ef.file_id::VARCHAR, ',' ORDER BY ef.file_id), 'None')
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'consumed'
		) AS  input_list,
		(SELECT COALESCE(STRING_AGG(ef.file_id::VARCHAR, ',' ORDER BY ef.file_id), 'None')  
			FROM execution_file ef
			WHERE ef.se_id = se.se_id and ef.transfer_type = 'produced'
		) AS output_list
	FROM service_execution se
	GROUP BY se.se_id ,se.activity_id
	ORDER BY se_id, activity_id, first_input_id
)
--select * from service_execution_with_input_output_list t1
update service_execution se
set task_id = (select ta.task_id 
					from service_execution_with_input_output_list t1
					join task ta on ta.activity_id = t1.activity_id and 
									ta.input_list  = t1.input_list and
									ta.output_list = t1.output_list
					where t1.se_id = se.se_id
				)
where se.task_id = -1
;


select * from task order by task_id desc;


select distinct workflow_execution_id, se_id, task_id from service_execution order by se_id desc;
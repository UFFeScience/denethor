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
			activity_id,
			first_input_id,
			first_output_id,
			input_count,
			output_count,
			input_list,
			output_list
	FROM service_execution_with_input_output_list
	ORDER BY activity_id, first_input_id
);


select * from task;


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
--select * from service_execution_with_input_output_list;
update service_execution se
set task_id = (select ta.task_id 
				from service_execution_with_input_output_list t1
				join task ta on ta.activity_id = t1.activity_id and ta.input_list = t1.input_list and ta.output_list = t1.output_list
				where t1.se_id = se.se_id
				)
;


select distinct se_id, task_id from service_execution order by 1;
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


select distinct workflow_execution_id, se_id, task_id, start_time from service_execution
order by se_id desc;

select distinct * from service_execution se
left outer join execution_file ef on ef.se_id = se.se_id
left outer join file f on f.file_id = ef.file_id
--join task ta on ta.task_id = se.task_id
--join execution_file ef on ef.se_id = se.se_id
where workflow_execution_id = 'weid_1735319150437' 
AND ef.transfer_type = 'consumed'
 --AND se.se_id in (148, 149, 150) 
order by se.se_id;




--- popular workflow_execution com dados de service_execution,
--- incluindo a contagem de arquivos de entrada da atividade 1
INSERT INTO workflow_execution (we_tag, workflow_id, start_time, end_time, duration, input_count, task_count, service_execution_count, input_list, runtime_data, info)
SELECT
	--ROW_NUMBER() OVER (ORDER BY workflow_execution_id, task_id) AS rownum,
		se.workflow_execution_id AS we_tag,
--		se.task_id,
--		se.activity_id,
		1 AS workflow_id,
		MIN(se.start_time) AS start_time,
		MAX(se.end_time) AS end_time,
		EXTRACT(EPOCH FROM (MAX(se.end_time) - MIN(se.start_time))) AS duration,
		SUM(case 
				when se.activity_id = 1 then se.consumed_files_count 
				else null
			end) AS input_count,
		count(distinct se.task_id) as task_count,
		count(*) as service_execution_count,
		STRING_AGG((case when se.activity_id = 1 then ef.file_id else null end)::VARCHAR, ',' ORDER BY ef.file_id) AS input_list,
		null AS runtime_data,
		'inital import from service_execution: 07-fev-2024-15:20' AS info
FROM 
    service_execution se
left outer join execution_file ef on ef.se_id = se.se_id
where ef.transfer_type = 'consumed'
group by se.workflow_execution_id--, se.task_id, se.activity_id
ORDER BY se.workflow_execution_id--, se.task_id, se.activity_id
;
--insert into task(activity_id, input_files) select activity_id, file_id_list as input_files from (
SELECT DISTINCT
		activity_id,
		first_file_id,
		file_id_list
FROM (
		SELECT 
			se.activity_id,
			se.se_id,
			(
				SELECT COALESCE(MIN(ef.file_id),0) first_file_id 
				FROM execution_file ef
				WHERE ef.se_id = se.se_id AND ef.transfer_type = 'consumed'
			),
			(
				SELECT COALESCE(STRING_AGG(ef.file_id::VARCHAR, ',' ORDER BY ef.file_id), '')
				FROM execution_file ef
				WHERE ef.se_id = se.se_id AND ef.transfer_type = 'consumed'
			) AS file_id_list
		FROM service_execution se
		JOIN workflow_activity wa ON wa.activity_id = se.activity_id
		GROUP BY se.se_id ,se.activity_id, file_id_list
	)
ORDER BY activity_id, first_file_id --)
;


select * from task;
-- set the locale to brazilian portuguese
SET lc_numeric = 'pt_BR';



select * from workflow;

select * from workflow_execution;

select * from provider_configuration;

-- service_execution

select * from vw_service_execution_info;

select * from vw_service_execution_info_last;


select 
	se.se_id,
	we.execution_tag,
	we.input_count,
	pr.provider_name,
	pc.memory_mb,
    wo.workflow_name, 
    wa.activity_name,
	se.request_id, 
    se.start_time, 
    se.end_time,
	to_char(se.duration,'fm9999990D00') AS duration,
    to_char(se.billed_duration,'fm9999990D00') AS billed_duration,
    to_char(se.init_duration,'fm9999990D00') AS init_duration,
    se.memory_size,
    se.max_memory_used, 
    se.consumed_files_count,
    se.produced_files_count, 
    se.consumed_files_size, 
    se.produced_files_size,
    to_char(se.consumed_files_transfer_duration,'fm9999990D00') AS consumed_files_transfer_duration,
    to_char(se.produced_files_transfer_duration,'fm9999990D00') AS produced_files_transfer_duration,
	(SELECT COALESCE(STRING_AGG(ef.file_id::VARCHAR, ',' ORDER BY ef.file_id), 'None')
		FROM execution_file ef
		WHERE ef.se_id = se.se_id and ef.transfer_type = 'consumed'
	) AS  consumed_files_list,
	(SELECT COALESCE(STRING_AGG(ef.file_id::VARCHAR, ',' ORDER BY ef.file_id), 'None')  
		FROM execution_file ef
		WHERE ef.se_id = se.se_id and ef.transfer_type = 'produced'
	) AS produced_files_list
FROM service_execution se
JOIN workflow_execution we ON se.we_id = we.we_id
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
JOIN workflow wo ON wo.workflow_id = wa.workflow_id
JOIN provider_configuration pc ON se.provider_conf_id = pc.conf_id
JOIN provider pr ON pr.provider_id = pc.provider_id
ORDER BY se.se_id ASC



-- files
SET lc_numeric = 'pt_BR';
SELECT 
    se.se_id,
    pr.provider_name,
    wo.workflow_name,
    wa.activity_name,
    fi.file_id,
    fi.file_name,
    fi.file_bucket,
    fi.file_path,
    fi.file_size,
    to_char(ef.transfer_duration,'fm9999999D99') AS transfer_duration,
    ef.transfer_type
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
JOIN workflow wo ON wo.workflow_id = wa.workflow_id
JOIN provider pr ON pr.provider_id = se.provider_id
JOIN execution_file ef ON ef.se_id = se.se_id
JOIN file fi ON fi.file_id = ef.file_id
--WHERE fi.file_name LIKE '%ORTHOMCL1000%'
--WHERE se.workflow_execution_id = 'weid_1735311414938'
ORDER BY se.se_id ASC, ef.transfer_type, fi.file_id ASC;



-- statistics
SELECT 
    se.se_id,
    pr.provider_name,
    wo.workflow_name,
    wa.activity_name,
    st.statistics_name,
    COALESCE(to_char(es.value_float,'fm9999999D99'),
                to_char(es.value_integer,'fm9999999D99'),
                es.value_string) AS value
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
JOIN workflow wo ON wo.workflow_id = wa.workflow_id
JOIN provider pr ON pr.provider_id = se.provider_id
JOIN execution_statistics es ON es.se_id = se.se_id
JOIN statistics st ON st.statistics_id = es.statistics_id
ORDER BY se.se_id, st.statistics_id;



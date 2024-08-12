-- service_execution
SET lc_numeric = 'pt_BR';
SELECT se.se_id, 
        pr.provider_name, 
        wo.workflow_name, 
        wa.activity_name, 
        se.request_id, 
        se.start_time, 
        se.end_time, 
        to_char(se.duration,'fm9999999D99') AS duration,
        to_char(se.billed_duration,'fm9999999D99') AS billed_duration,
        to_char(se.init_duration,'fm9999999D99') AS init_duration,
        se.memory_size, se.max_memory_used, 
        se.consumed_files_count,
        se.consumed_files_size, 
        to_char(se.consumed_files_transfer_duration,'fm9999999D99') AS consumed_files_transfer_duration,
        se.produced_files_count, 
        se.produced_files_size,
        to_char(se.produced_files_transfer_duration,'fm9999999D99') AS produced_files_transfer_duration
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
JOIN workflow wo ON wo.workflow_id = wa.workflow_id
JOIN provider pr ON pr.provider_id = se.provider_id
ORDER BY se.se_id ASC;



-- files
SET lc_numeric = 'pt_BR';
SELECT se.se_id,
        pr.provider_name,
        wo.workflow_name,
        wa.activity_name,
        fi.file_id,
        fi.file_name,
        fi.file_size,
        fi.file_path,
        fi.file_bucket,
        to_char(ef.transfer_duration,'fm9999999D99') AS transfer_duration,
        ef.transfer_type
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
JOIN workflow wo ON wo.workflow_id = wa.workflow_id
JOIN provider pr ON pr.provider_id = se.provider_id
JOIN execution_file ef ON ef.se_id = se.se_id
JOIN file fi ON fi.file_id = ef.file_id
--WHERE fi.file_name LIKE '%ORTHOMCL1000%'
ORDER BY se.se_id ASC, fi.file_id ASC;

-- statistics
SET lc_numeric = 'pt_BR';
SELECT se.se_id,
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



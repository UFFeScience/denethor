--view file_type: dynamic_files + tatic_files
CREATE OR REPLACE VIEW vw_file_type AS
    SELECT distinct
        ef.se_id, 
        ef.file_id, 
        'dynamic' AS file_type
    FROM execution_file ef
    WHERE ef.transfer_type = 'produced'
    
    UNION
    
    SELECT distinct
        ef.se_id, 
        ef.file_id, 
        'static' AS file_type
    FROM execution_file ef
    WHERE ef.transfer_type = 'consumed'
    AND ef.file_id NOT IN (
        SELECT ef2.file_id
        FROM execution_file ef2
        WHERE ef2.transfer_type = 'produced'
);

DROP VIEW IF EXISTS vw_service_execution_info_last;
DROP VIEW IF EXISTS vw_service_execution_info;
CREATE OR REPLACE VIEW  vw_service_execution_info AS 
SELECT 
    se.se_id,
    se.workflow_execution_id,
    se.task_id,
    pr.provider_name, 
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
    se.consumed_files_size, 
    to_char(se.consumed_files_transfer_duration,'fm9999990D00') AS consumed_files_transfer_duration,
    se.produced_files_count, 
    se.produced_files_size,
    to_char(se.produced_files_transfer_duration,'fm9999990D00') AS produced_files_transfer_duration
FROM service_execution se
JOIN workflow_activity wa ON wa.activity_id = se.activity_id
JOIN workflow wo ON wo.workflow_id = wa.workflow_id
JOIN provider pr ON pr.provider_id = se.provider_id
ORDER BY se.se_id ASC;


CREATE OR REPLACE VIEW vw_service_execution_info_last AS
    SELECT * 
    FROM vw_service_execution_info vwse
    WHERE vwse.workflow_execution_id = (SELECT se.workflow_execution_id
                                    FROM service_execution se
                                    WHERE se.end_time = (SELECT max(se2.end_time)
                                                            FROM service_execution se2))
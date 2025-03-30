--view file_type: dynamic_files + static_files
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


-- view service_execution_info: complete information about service execution
DROP VIEW IF EXISTS vw_service_execution_info;

CREATE OR REPLACE VIEW  vw_service_execution_info AS 
    SELECT 
        se.se_id,
        we.we_id,
        we.execution_tag,
        we.input_count,
        pr.provider_id,
        pr.provider_name,
        pc.memory_mb,
        wo.workflow_id,
        wo.workflow_name, 
        wa.activity_id,
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
    ORDER BY se.se_id ASC;


-- view service_execution_info_last: last service execution
CREATE OR REPLACE VIEW vw_service_execution_info_last AS
    SELECT * 
    FROM vw_service_execution_info vwse
    WHERE vwse.workflow_execution_id = (SELECT se.workflow_execution_id
                                    FROM service_execution se
                                    WHERE se.end_time = (SELECT max(se2.end_time)
                                                            FROM service_execution se2))
;



--NOVO MODELO: 23/02/2025
--view task: information about tasks
DROP VIEW IF EXISTS vw_task;
CREATE OR REPLACE VIEW vw_task AS
    WITH 
    service_execution_detail AS ( 
        SELECT 
            se.se_id,
            se.activity_id,
            ef.transfer_type,
            COALESCE(MIN(ef.file_id),0) AS first_id,
            COUNT(ef.file_id) AS file_count,
            COALESCE(STRING_AGG(ef.file_id::VARCHAR, ',' ORDER BY ef.file_id), 'None') AS  file_list
        FROM service_execution se
        LEFT OUTER JOIN execution_file ef ON ef.se_id = se.se_id
        GROUP BY se.se_id, se.activity_id, ef.transfer_type
        ORDER BY first_id, se.activity_id
    )
    SELECT min(t1.se_id) as task_id,
        t1.activity_id,
        count(*) as execution_count,
        t1.file_count as consumed_files_count,
        t2.file_count as produced_files_count,
        t1.file_list as consumed_files_list,
        t2.file_list as produced_files_list
    FROM service_execution_detail t1
    LEFT OUTER JOIN service_execution_detail t2 ON t1.se_id = t2.se_id
    WHERE t1.transfer_type = 'consumed' AND t2.transfer_type = 'produced'
    GROUP BY t1.activity_id,
            consumed_files_count,
            produced_files_count,
            consumed_files_list,
            produced_files_list			
    ORDER BY task_id, t1.activity_id, consumed_files_count, produced_files_count
;


-- view service_execution_task: relationship between service execution and task
CREATE OR REPLACE VIEW vw_service_execution_task AS
    SELECT
        se.se_id,
        ta.task_id
    FROM vw_service_execution_info se
    JOIN vw_task ta ON se.activity_id = ta.activity_id AND
                    se.consumed_files_list = ta.consumed_files_list AND
                    se.produced_files_list = ta.produced_files_list
    ORDER BY se.se_id	
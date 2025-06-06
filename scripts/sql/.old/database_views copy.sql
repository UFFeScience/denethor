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
DROP VIEW IF EXISTS vw_service_execution_info CASCADE;

CREATE OR REPLACE VIEW  vw_service_execution_info AS 
    SELECT 
        se.se_id,
        we.we_id,
        we.execution_tag,
        we.start_time as workflow_start_time,
        we.end_time as workflow_end_time,
        we.duration as workflow_duration, 
        we.input_count as workflow_input_count,
        pr.provider_id,
        pr.provider_name,
        pc.memory_mb as provider_memory_mb,
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
            WHERE ef.se_id = se.se_id AND ef.transfer_type = 'consumed'
        ) AS  consumed_files_list,
        (SELECT COALESCE(STRING_AGG(ef.file_id::VARCHAR, ',' ORDER BY ef.file_id), 'None')  
            FROM execution_file ef
            WHERE ef.se_id = se.se_id AND ef.transfer_type = 'produced'
        ) AS produced_files_list
    FROM service_execution se
    JOIN workflow_execution we ON se.we_id = we.we_id
    JOIN workflow_activity wa ON wa.activity_id = se.activity_id
    JOIN workflow wo ON wo.workflow_id = wa.workflow_id
    JOIN provider_configuration pc ON se.provider_conf_id = pc.conf_id
    JOIN provider pr ON pr.provider_id = pc.provider_id
    ORDER BY se.se_id ASC;





DROP VIEW IF EXISTS vw_service_execution_detail2;
CREATE OR REPLACE VIEW vw_service_execution_detail2 AS ( 
    WITH service_execution_files AS (
        SELECT 
            se.se_id,
            ef.transfer_type,
            COALESCE(MIN(ef.file_id),0) AS first_id,
            COUNT(ef.file_id) AS file_count,
            COALESCE(STRING_AGG(ef.file_id::VARCHAR, ',' ORDER BY ef.file_id), 'None') AS  file_list
        FROM service_execution se
        LEFT OUTER JOIN execution_file ef ON ef.se_id = se.se_id
        GROUP BY se.se_id, ef.transfer_type
        ORDER BY se.se_id
    )
    SELECT 
        se.se_id,
        we.we_id,
        we.execution_tag,
        we.start_time as workflow_start_time,
        we.end_time as workflow_end_time,
        we.duration as workflow_duration, 
        we.input_count as workflow_input_count,
        pr.provider_id,
        pr.provider_name,
        pc.memory_mb as provider_memory_mb,
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
        
        -- t1.se_id,
        -- t1.activity_id,
        -- t1.file_count as input_count,
        -- t2.file_count as output_count,
        t1.file_list as consumed_files_list,
        t2.file_list as produced_files_list
    FROM service_execution se
    JOIN workflow_execution we ON se.we_id = we.we_id
    JOIN workflow_activity wa ON wa.activity_id = se.activity_id
    JOIN workflow wo ON wo.workflow_id = wa.workflow_id
    JOIN provider_configuration pc ON se.provider_conf_id = pc.conf_id
    JOIN provider pr ON pr.provider_id = pc.provider_id
    LEFT OUTER JOIN service_execution_files t1 ON se.se_id = t1.se_id
    LEFT OUTER JOIN service_execution_files t2 ON se.se_id = t2.se_id
    WHERE t1.transfer_type = 'consumed' AND 
          t2.transfer_type = 'produced'
    ORDER BY se.se_id
);


-- view vw_service_execution_info_recent: most recent service execution
DROP VIEW IF EXISTS vw_service_execution_info_recent;
CREATE OR REPLACE VIEW vw_service_execution_info_recent AS
    SELECT * 
    FROM vw_service_execution_info
    WHERE we_id = (
        SELECT max(we_id) FROM service_execution
    )
;



--NOVO MODELO: 23/02/2025
--view task: information about tasks
select * from vw_task;
DROP VIEW IF EXISTS vw_task CASCADE;
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
        1 as task_type,
        t1.file_count as input_count,
        t2.file_count as output_count,
        t1.file_list as input_list,
        t2.file_list as output_list
    FROM service_execution_detail t1
    LEFT OUTER JOIN service_execution_detail t2 ON t1.se_id = t2.se_id
    WHERE t1.transfer_type = 'consumed' AND t2.transfer_type = 'produced'
    GROUP BY t1.activity_id,
            input_count,
            output_count,
            input_list,
            output_list			
    ORDER BY task_id, t1.activity_id, input_count, output_count
;

-- view service_execution_task: relationship between service execution and task
CREATE OR REPLACE VIEW vw_service_execution_task AS
    SELECT
        se.se_id,
        ta.task_id
    FROM vw_service_execution_info se
    JOIN vw_task ta ON se.activity_id = ta.activity_id AND
                    se.consumed_files_list = ta.input_list AND
                    se.produced_files_list = ta.output_list
    ORDER BY se.se_id
;










-------------------- Materialized Views --------------------
DROP MATERIALIZED VIEW IF EXISTS vw_task_mv CASCADE;
CREATE MATERIALIZED VIEW vw_task_mv AS
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
        1 as task_type,
        t1.file_count as input_count,
        t2.file_count as output_count,
        t1.file_list as input_list,
        t2.file_list as output_list
    FROM service_execution_detail t1
    LEFT OUTER JOIN service_execution_detail t2 ON t1.se_id = t2.se_id
    WHERE t1.transfer_type = 'consumed' AND t2.transfer_type = 'produced'
    GROUP BY t1.activity_id,
            input_count,
            output_count,
            input_list,
            output_list			
    ORDER BY task_id, t1.activity_id, input_count, output_count
WITH DATA;

-- Optional: Indexes to improve query performance
CREATE UNIQUE INDEX idx_vw_task_task_id_unique ON vw_task_mv (task_id);
CREATE INDEX idx_vw_task_activity_id ON vw_task_mv (activity_id);
CREATE INDEX idx_vw_task_input_list ON vw_task_mv (input_list);
CREATE INDEX idx_vw_task_output_list ON vw_task_mv (output_list);





DROP MATERIALIZED VIEW IF EXISTS vw_service_execution_task_mv CASCADE;
CREATE MATERIALIZED VIEW vw_service_execution_task_mv AS
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
    SELECT ta.task_id,
           t1.se_id as se_id
    FROM service_execution_detail t1
    LEFT OUTER JOIN service_execution_detail t2 ON t1.se_id = t2.se_id
    JOIN vw_task_mv ta ON t1.activity_id = ta.activity_id AND
                    t1.file_list = ta.input_list AND
                    t2.file_list = ta.output_list
    WHERE t1.transfer_type = 'consumed' AND t2.transfer_type = 'produced'
    ORDER BY t1.se_id
WITH DATA;

DROP VIEW IF EXISTS vw_service_execution_task;
CREATE OR REPLACE VIEW vw_service_execution_task AS
    SELECT
        ta.task_id,
        se.se_id
    FROM vw_service_execution_info se
    JOIN vw_task ta ON se.activity_id = ta.activity_id AND
                    se.consumed_files_list = ta.input_list AND
                    se.produced_files_list = ta.output_list
    ORDER BY se.se_id
;

-- Create indexes to improve query performance
CREATE UNIQUE INDEX idx_vw_service_execution_task_se_id_task_id ON vw_service_execution_task_mv (se_id, task_id);
CREATE INDEX idx_vw_service_execution_task_se_id ON vw_service_execution_task_mv (se_id);
CREATE INDEX idx_vw_service_execution_task_task_id ON vw_service_execution_task_mv (task_id);

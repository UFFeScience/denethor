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



-- vw_service_execution_files_agg: aggregated information about service execution files
-- This view aggregates information about service execution files, including the first file ID, file count, and file list.
--DROP VIEW IF EXISTS vw_service_execution_files_agg;
CREATE OR REPLACE VIEW vw_service_execution_files_agg AS ( 
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
    ORDER BY se.se_id
);


-- vw_service_execution_detail: detailed information about service execution
-- This view provides detailed information about service execution, including workflow execution details, provider information, and file transfer details.
--DROP VIEW IF EXISTS vw_service_execution_detail;
CREATE OR REPLACE VIEW vw_service_execution_detail AS ( 
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
        pr.provider_tag,
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
        t1.file_list as consumed_files_list,
        t2.file_list as produced_files_list
    FROM service_execution se
    JOIN workflow_execution we ON se.we_id = we.we_id
    JOIN workflow_activity wa ON wa.activity_id = se.activity_id
    JOIN workflow wo ON wo.workflow_id = wa.workflow_id
    JOIN provider_configuration pc ON se.provider_conf_id = pc.conf_id
    JOIN provider pr ON pr.provider_id = pc.provider_id
    LEFT OUTER JOIN vw_service_execution_files_agg t1 ON se.se_id = t1.se_id
    LEFT OUTER JOIN vw_service_execution_files_agg t2 ON se.se_id = t2.se_id
    WHERE t1.transfer_type = 'consumed' AND 
          t2.transfer_type = 'produced'
    ORDER BY se.se_id
);




--view task: information about tasks
-- vw_task2: information about tasks
-- This view provides information about tasks, including task ID, activity ID, execution count, task type, input and output counts, and file lists.
--DROP VIEW IF EXISTS vw_task;
CREATE OR REPLACE VIEW vw_task AS
    SELECT 
        min(t1.se_id) as task_id,
        t1.activity_id as activity_id,
        count(*) as execution_count,
        1 as task_type,
        t1.file_count as input_count,
        t2.file_count as output_count,
        t1.file_list as input_list,
        t2.file_list as output_list
    FROM vw_service_execution_files_agg t1
    LEFT OUTER JOIN vw_service_execution_files_agg t2 ON t1.se_id = t2.se_id
    WHERE t1.transfer_type = 'consumed' AND t2.transfer_type = 'produced'
    GROUP BY t1.activity_id,
             input_count,
             output_count,
             input_list,
             output_list			
    ORDER BY task_id
;

-- view service_execution_task: relationship between service execution and task
-- This view provides the relationship between service execution and task, including service execution ID and task ID.
--DROP VIEW IF EXISTS vw_service_execution_task;
CREATE OR REPLACE VIEW vw_service_execution_task AS
    SELECT
        t1.se_id,
        ta.task_id
    FROM vw_task ta
    LEFT OUTER JOIN vw_service_execution_files_agg t1 ON t1.activity_id = ta.activity_id AND t1.file_list = ta.input_list
    LEFT OUTER JOIN vw_service_execution_files_agg t2 ON t2.activity_id = ta.activity_id AND t2.file_list = ta.output_list
    WHERE t1.se_id = t2.se_id
    ORDER BY t1.se_id
;

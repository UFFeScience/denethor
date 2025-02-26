--view file_type: dynamic_files + static_files
CREATE OR REPLACE VIEW vw_file_type AS
    SELECT distinct
        ef.se_id,
        ef.file_id,
        'dynamic' AS file_type
    FROM backup_19_02_2025.execution_file ef
    WHERE ef.transfer_type = 'produced'
    
    UNION
    
    SELECT distinct
        ef.se_id,
        ef.file_id,
        'static' AS file_type
    FROM backup_19_02_2025.execution_file ef
    WHERE ef.transfer_type = 'consumed'
    AND ef.file_id NOT IN (
        SELECT ef2.file_id
        FROM backup_19_02_2025.execution_file ef2
        WHERE ef2.transfer_type = 'produced'
);

DROP VIEW IF EXISTS vw_file_type;
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
;



--NOVO MODELO: 23/02/2025
CREATE OR REPLACE VIEW vw_task AS
    with 
        service_execution_input as ( 
            SELECT 
                se.se_id,
                se.activity_id,
                COALESCE(MIN(ef.file_id),0) AS first_input_id,
                COUNT(ef.file_id) AS input_count,
                COALESCE(STRING_AGG(ef.file_id::CHAR(30), ',' ORDER BY ef.file_id), 'None') AS  input_list
            FROM backup_19_02_2025.service_execution se
            LEFT OUTER JOIN backup_19_02_2025.execution_file ef on ef.se_id = se.se_id and ef.transfer_type = 'consumed'
            GROUP BY se.id, se.activity_id
            ORDER BY first_input_id, se.activity_id
        ),
        service_execution_output as ( 
            SELECT 
                se.se_id,
                se.activity_id,
                COALESCE(MIN(ef.file_id),0) AS first_output_id,
                COUNT(ef.file_id) AS output_count,
                COALESCE(STRING_AGG(ef.file_id::CHAR(30), ',' ORDER BY ef.file_id), 'None') AS  output_list
            FROM backup_19_02_2025.service_execution se
            LEFT OUTER JOIN backup_19_02_2025.execution_file ef on ef.se_id = se.se_id and ef.transfer_type = 'produced'
            GROUP BY se.id, se.activity_id
            ORDER BY first_output_id, se.activity_id
        )
    select min(t1.se_id) as task_id,
           count(*) as execution_count,
           t1.activity_id,
           t1.input_count,
           t1.input_list,
           t2.output_count,
           t2.output_list
    FROM service_execution_input t1
    LEFT OUTER JOIN service_execution_output t2 ON t1.se_id = t2.se_id
    GROUP BY t1.activity_id,
             t1.input_count,
             t1.input_list,
             t2.output_count,
             t2.output_list			
    order by task_id, t1.activity_id, t1.input_count
;
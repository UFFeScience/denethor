SELECT * FROM vw_service_execution_info_last ORDER BY se_id;

SELECT *
FROM service_execution
WHERE
    workflow_execution_id = 'weid_1729872039000';

-- Exibir os dados de execução do workflow
SELECT DISTINCT
    we_id,
    execution_tag,
    workflow_start_time,
    workflow_duration,
    workflow_input_count,
    provider_id,
    provider_name,
    provider_memory_mb
FROM vw_service_execution_info
ORDER BY we_id;

--DELETE DE REGISTROS DEPENDENTES PARA UM DETERMINADO EXECUTION_TAG
DELETE FROM execution_file
WHERE
    se_id IN (
        SELECT se_id
        FROM service_execution se
        JOIN workflow_execution we ON se.we_id = we.we_id
        WHERE
            execution_tag = 'wetag_1743630589148'
    );

DELETE FROM execution_statistics
WHERE
    se_id IN (
        SELECT se_id
        FROM service_execution se
        JOIN workflow_execution we ON se.we_id = we.we_id
        WHERE
            execution_tag = 'wetag_1743630589148'
    );

DELETE FROM "file"
WHERE
    file_id NOT IN (
        SELECT file_id
        FROM execution_file
    );

DELETE FROM "statistics"
WHERE
    statistics_id NOT IN (
        SELECT statistics_id
        FROM execution_statistics
    );

DELETE FROM service_execution
WHERE
    se_id IN (
        SELECT se_id
        FROM service_execution se
        JOIN workflow_execution we ON se.we_id = we.we_id
        WHERE
            execution_tag = 'wetag_1743630589148'
    );

DELETE workflow_execution we
WHERE
    execution_tag = 'wetag_1743630589148';




-- AJUSTE PARA 2 ENTRADAS
-- ajustar dados da execução ec2 com informações de arquivos da execução do lambda
select * from vw_service_execution_info sei
where execution_tag in ('wetag_1743638228939', 'wetag_1743630589148')
order by se_id
;

SELECT STRING_AGG(se_id::TEXT, ', ' ORDER BY se_id) AS se_id_list
FROM vw_service_execution_info sei
WHERE execution_tag IN ('wetag_1743638228939', 'wetag_1743630589148')
;

-- service_execution com tasks associadas
select se.se_id, st.se_id, ta.* 
from service_execution se
left outer join vw_service_execution_task st on se.se_id = st.se_id 
left outer join vw_task ta on st.task_id = ta.task_id
order by se.se_id desc;


WITH source_data AS (
    SELECT se_id, consumed_files_count, consumed_files_size, consumed_files_transfer_duration,
           produced_files_count, produced_files_size, produced_files_transfer_duration,
           ROW_NUMBER() OVER (ORDER BY se_id) AS row_num
    FROM service_execution
    WHERE se_id IN (52, 53, 54, 55, 56, 57, 58)
),
target_data AS (
    SELECT se_id, ROW_NUMBER() OVER (ORDER BY se_id) AS row_num
    FROM service_execution
    WHERE se_id IN (200, 201, 202, 203, 204, 205, 206)
)
UPDATE service_execution AS se
SET
    consumed_files_count = src.consumed_files_count,
    consumed_files_size = src.consumed_files_size,
    consumed_files_transfer_duration = src.consumed_files_transfer_duration,
    produced_files_count = src.produced_files_count,
    produced_files_size = src.produced_files_size,
    produced_files_transfer_duration = src.produced_files_transfer_duration
FROM source_data AS src
JOIN target_data AS tgt ON src.row_num = tgt.row_num
WHERE se.se_id = tgt.se_id;



WITH
source_data AS (
    SELECT 
        se_id,
        ROW_NUMBER() OVER (ORDER BY se_id) AS row_num
    FROM service_execution
	WHERE se_id IN (52, 53, 54, 55, 56, 57, 58)
),
target_data AS (
    SELECT 
        se_id,
        ROW_NUMBER() OVER (ORDER BY se_id) AS row_num
    FROM service_execution
    WHERE se_id IN (200, 201, 202, 203, 204, 205, 206)
),
source_file_data AS (
    SELECT 
        ef.se_id,
        ef.file_id,
        ef.transfer_duration,
        ef.transfer_type,
        sd.row_num
    FROM execution_file ef
	JOIN source_data sd on ef.se_id = sd.se_id
    WHERE ef.se_id IN (52, 53, 54, 55, 56, 57, 58)
)
INSERT INTO execution_file (se_id, file_id, transfer_duration, transfer_type)
SELECT 
    tgt.se_id,
    sfd.file_id,
    sfd.transfer_duration,
    sfd.transfer_type
FROM source_file_data sfd
JOIN target_data AS tgt ON sfd.row_num = tgt.row_num;
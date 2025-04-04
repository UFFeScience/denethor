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
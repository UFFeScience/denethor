-- registros com transfer_duration de subtree_files na atividade maf_db_creator = 0
-- executados em fx com cache local desses arquivos para agilizar o processo
-- ajustar pegando o tempo de file_metrics
SELECT
    se.se_id,
    se.we_id,
    we.execution_tag,
    p.provider_name,
    se.activity_id,
    f.file_id,
    f.file_name,
    f.file_size,
    ef.transfer_type,
    ef.transfer_duration,
    fm.file_name,
    fm.metric_type,
    avg(fm.duration_ms) duration_ms,
    avg(fm.normalized_duration_ms) normalized_duration_ms
FROM
    service_execution se
    JOIN workflow_execution we ON se.we_id = we.we_id
    JOIN provider_configuration pc ON pc.conf_id = se.provider_conf_id
    JOIN provider p ON p.provider_id = pc.provider_id
    JOIN execution_file ef ON ef.se_id = se.se_id
    JOIN file f ON f.file_id = ef.file_id
    LEFT OUTER JOIN file_metrics fm ON f.file_name = fm.file_name
    AND fm.metric_type = CASE
        WHEN ef.transfer_type = 'consumed' THEN 'download'
        WHEN ef.transfer_type = 'produced' THEN 'upload'
    END
WHERE
    ef.transfer_duration = 0
    AND p.provider_id = 1
GROUP BY
    se.se_id,
    se.we_id,
    we.execution_tag,
    p.provider_name,
    se.activity_id,
    f.file_id,
    f.file_name,
    f.file_size,
    ef.transfer_type,
    ef.transfer_duration,
    fm.file_name,
    fm.metric_type
ORDER BY se.we_id;
--263285

-- Atualizar ef.transfer_duration quando for zero
UPDATE execution_file ef
SET
    transfer_duration = COALESCE(t1.avg_duration_ms, 0)
FROM (
        SELECT
            f.file_id, f.file_name, CASE
                WHEN fm.metric_type = 'download' THEN 'consumed'
                WHEN fm.metric_type = 'upload' THEN 'produced'
            END AS metric_type, AVG(fm.normalized_duration_ms) AS avg_duration_ms
        FROM file_metrics fm
            JOIN file f ON f.file_name = fm.file_name
        GROUP BY
            f.file_id, f.file_name, fm.metric_type
    ) t1
WHERE
    ef.file_id = t1.file_id
    AND ef.transfer_type = t1.metric_type
    AND ef.transfer_duration = 0
    AND EXISTS (
        SELECT 1
        FROM
            service_execution se
            JOIN provider_configuration pc ON se.provider_conf_id = pc.conf_id
        WHERE
            se.se_id = ef.se_id
            AND pc.provider_id = 1
    );

SELECT we.we_id, we.input_count, se.*
FROM
    execution_file ef
    JOIN service_execution se ON ef.se_id = se.se_id
    JOIN workflow_execution we ON we.we_id = se.we_id
WHERE
    ef.transfer_duration = 0
    --group by se.we_id
;
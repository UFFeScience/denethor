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






-- atualizando service_execution para salvar os valores originais dos campos
UPDATE service_execution
SET original_values = json_build_object(
    'se_id', se_id,
    'we_id', we_id,
    'activity_id', activity_id,
    'provider_conf_id', provider_conf_id,
    'start_time', start_time,
    'end_time', end_time,
    'duration', duration,
    'billed_duration', billed_duration,
    'init_duration', init_duration,
    'memory_size', memory_size,
    'max_memory_used', max_memory_used,
    'consumed_files_count', consumed_files_count,
    'consumed_files_size', consumed_files_size,
    'consumed_files_transfer_duration', consumed_files_transfer_duration,
    'produced_files_count', produced_files_count,
    'produced_files_size', produced_files_size,
    'produced_files_transfer_duration', produced_files_transfer_duration
)::TEXT
WHERE se_id IN (
	select se_id
	from service_execution se
	join provider_configuration pc on pc.conf_id = se.provider_conf_id
	where se.consumed_files_transfer_duration = 0 and
		  pc.provider_id = 1
)

-- Update consumed_files_transfer_duration in service_execution
UPDATE service_execution se
SET updated_consumed_duration = TRUE,
    consumed_files_transfer_duration = (
        SELECT SUM(ef.transfer_duration)
        FROM execution_file ef
        WHERE ef.se_id = se.se_id
        AND ef.transfer_type = 'consumed'
)
WHERE se_id IN (
	select se_id
	from service_execution se
	join provider_configuration pc on pc.conf_id = se.provider_conf_id
	where se.consumed_files_transfer_duration = 0 and
		  pc.provider_id = 1
);

-- Para os casos quem que consumed_durations foi atualizado, mas ainda ficou com valor 0
-- Indica que o execution_file não tinha transfer_duration atualizado
-- Update consumed_files_transfer_duration in service_execution
UPDATE service_execution se
SET updated_consumed_duration = FALSE
WHERE se_id IN (
    select se_id
    from service_execution se
    join provider_configuration pc on pc.conf_id = se.provider_conf_id
    where se.consumed_files_transfer_duration = 0 and
          pc.provider_id = 1
);


-- Update duration and billed_duration in service_execution to add consumed_files_transfer_duration to its current value
UPDATE service_execution
SET 
    updated_duration = TRUE,
    duration = duration + COALESCE(consumed_files_transfer_duration, 0),
    updated_billed_duration = TRUE,
    billed_duration = CEIL(duration + COALESCE(consumed_files_transfer_duration, 0)),
WHERE 
    updated_consumed_duration is TRUE and
    updated_duration is FALSE



-- validando que os valores ajustados de duration e billed_duration estão coerentes com os originais + consumed_duration
select * from (
	select (t.duration - t.consumed_duration - t.original_duration)::int as duration_diff,
			(t.billed_duration - t.consumed_duration - t.original_billed_duration)::int as billed_duration_diff, 
			t.* 
	from (
		select se.se_id, se.we_id, se.duration, (se.original_values::jsonb->>'duration')::numeric as original_duration, 
		se.billed_duration, (se.original_values::jsonb->>'billed_duration')::numeric as original_billed_duration,
		se.consumed_files_transfer_duration as consumed_duration,
		se.original_values
		from service_execution se
		join provider_configuration pc on pc.conf_id = se.provider_conf_id
		where updated_consumed_duration is TRUE and
			  pc.provider_id = 1
			  --and se.consumed_files_transfer_duration = 0
			  --and se.original_values is not null
		) t
	)
where ABS(duration_diff) > 1 or
		ABS(billed_duration_diff) > 1
order by we_id;
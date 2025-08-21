select count(distinct file_name) from file_metrics;
select * from file_metrics order by file_name;

select count(distinct file_name) from vw_file_metrics_transfer_duration;
select * from vw_file_metrics_transfer_duration order by file_name;

select distinct f.file_name, ef.transfer_type 
from file f
join execution_file ef on ef.file_id = f.file_id
where f.file_name not like 'maf%' --2185

-- registros com transfer_duration de subtree_files na atividade maf_db_creator = 0
-- executados em fx com cache local desses arquivos para agilizar o processo
-- ajustar pegando o tempo de file_metrics
SELECT * FROM (
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
	    vwfm.file_name,
	    vwfm.metric_type,
	    avg(vwfm.duration_ms) avg_duration_ms,
	    avg(vwfm.normalized_duration_ms) avg_normalized_duration_ms,
		vwfm.avg_transfer_duration as avg_duration_by_range,
		vwfm.p50_transfer_duration as p50_duration_by_range
	FROM
	    service_execution se
	    JOIN workflow_execution we ON se.we_id = we.we_id
	    JOIN provider_configuration pc ON pc.conf_id = se.provider_conf_id
	    JOIN provider p ON p.provider_id = pc.provider_id
	    JOIN execution_file ef ON ef.se_id = se.se_id
	    JOIN file f ON f.file_id = ef.file_id
	    LEFT OUTER JOIN vw_file_metrics_transfer_duration vwfm ON vwfm.file_name = f.file_name AND vwfm.transfer_type = ef.transfer_type
	WHERE
	    ef.transfer_duration = 0 AND
	    p.provider_id = 1 AND
		se.we_id in (68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,
							 135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,
							 201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256
							)
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
	    vwfm.file_name,
	    vwfm.metric_type,
		avg_transfer_duration,
		p50_transfer_duration
		)
ORDER BY ABS(avg_duration_by_range - p50_duration_by_range) desc;
--263285



-- Atualizar ef.transfer_duration quando for zero
UPDATE execution_file ef
SET
    transfer_duration = COALESCE(t1.avg_duration_by_range, 0)
FROM (
        SELECT
            f.file_id, 
			f.file_name,
			f.file_size,
			vwfm.transfer_type,
			vwfm.avg_transfer_duration as avg_duration_by_range,
			count(*) as obs
        FROM vw_file_metrics_transfer_duration vwfm
		JOIN file f ON f.file_name = vwfm.file_name
		JOIN execution_file ef on ef.file_id = f.file_id and ef.transfer_type = vwfm.transfer_type
        GROUP BY
            f.file_id, f.file_name, f.file_size, vwfm.transfer_type, vwfm.avg_transfer_duration
    ) t1
WHERE
    ef.file_id = t1.file_id
    AND ef.transfer_type = t1.transfer_type
    AND ef.transfer_duration = 0
    AND EXISTS (
        SELECT 1
        FROM
            service_execution se
            JOIN provider_configuration pc ON se.provider_conf_id = pc.conf_id
        WHERE
            se.se_id = ef.se_id AND
			pc.provider_id = 1 AND
			se.we_id in (68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,
					 135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,
					 201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256
					)
);	-- UPDATE 645820



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
		  pc.provider_id = 1 and
		  se.we_id in (68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,
				 135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,
				 201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256
				)
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
		  pc.provider_id = 1 and
		  se.we_id in (68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,
				 135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,
				 201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256
				)
); --UPDATE 4155




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
          pc.provider_id = 1 and
		  se.we_id in (68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,
				 135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,
				 201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256
				)
);


-- Update duration and billed_duration in service_execution to add consumed_files_transfer_duration to its current value
UPDATE service_execution
SET 
    updated_duration = TRUE,
    duration = duration + COALESCE(consumed_files_transfer_duration, 0),
    updated_billed_duration = TRUE,
    billed_duration = CEIL(duration + COALESCE(consumed_files_transfer_duration, 0))
WHERE 
    updated_consumed_duration is TRUE and
    updated_duration is FALSE
;


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
			  --and 
			  --se.consumed_files_transfer_duration <> 0 and
			  --se.original_values is not null
		) t
	)
where ABS(duration_diff) > 1 or
		ABS(billed_duration_diff) > 1
order by we_id;



select * from service_execution se
join provider_configuration pc on pc.conf_id = se.provider_conf_id
where se.consumed_files_transfer_duration = 0 and
          pc.provider_id = 1 and
		  se.we_id in (68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,
				 135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,
				 201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256
				)







































select 
	se.se_id,
	se.we_id,
	we.execution_tag,
	se.start_time,
	se.end_time,
	se.duration,
	se.billed_duration,
	se.init_duration,
	f.file_name, 
	se.consumed_files_count,
	se.consumed_files_size,
	se.consumed_files_transfer_duration,
	se.produced_files_count,
	se.produced_files_size,
	se.produced_files_transfer_duration,
	SUM(ef.transfer_duration) as sum_consumed_duration,
	se.updated_consumed_duration,
	se.updated_duration,
	se.updated_billed_duration
from service_execution se
join workflow_execution we on we.we_id = se.we_id
left outer join execution_file ef on ef.se_id = se.se_id
left outer join file f on f.file_id = ef.file_id
where 
	se.we_id in (135,136,137,138,139)
	and se.activity_id = 3 
	and ef.transfer_type = 'consumed'
	--and se.consumed_files_transfer_duration = 0
	and se.provider_conf_id < 6
group by
se.se_id,
	se.we_id,
	we.execution_tag,
	se.start_time,
	se.end_time,
	se.duration,
	se.billed_duration,
	se.init_duration,
	f.file_name, 
	se.consumed_files_count,
	se.consumed_files_size,
	se.consumed_files_transfer_duration,
	se.produced_files_count,
	se.produced_files_size,
	se.produced_files_transfer_duration,
	se.updated_consumed_duration,
	se.updated_duration,
	se.updated_billed_duration
order by se.se_id
;

-- apenas atividade com id=3 estão com tempo de consumo de arquivos zerado para execução em função
select distinct se.activity_id
from service_execution se
join provider_configuration pc on pc.conf_id = se.provider_conf_id
where se.consumed_files_transfer_duration = 0
and pc.provider_id = 1
order by se.activity_id;

--atualizando service_execution para salvar os valores originais dos campos
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
);

-- Update consumed_files_transfer_duration in service_execution
UPDATE service_execution se
SET consumed_files_transfer_duration = (
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


UPDATE service_execution se
SET updated_consumed_duration = FALSE
WHERE se_id IN (
    select se_id
    from service_execution se
    join provider_configuration pc on pc.conf_id = se.provider_conf_id
    where se.consumed_files_transfer_duration = 0 and
          pc.provider_id = 1
);


UPDATE service_execution
SET 
    updated_duration = TRUE,
    duration = duration + COALESCE(consumed_files_transfer_duration, 0),
    updated_billed_duration = TRUE,
    billed_duration = CEIL(duration + COALESCE(consumed_files_transfer_duration, 0))
WHERE 
    updated_consumed_duration is TRUE and
    updated_duration is FALSE
;

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




	  
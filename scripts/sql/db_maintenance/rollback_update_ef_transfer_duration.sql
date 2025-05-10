-- service execution atualizados
select * from service_execution se
where 
(se.updated_consumed_duration = true and original_values is null ) 
OR 
(se.updated_consumed_duration = false and original_values is not null and consumed_files_transfer_duration <> 0)
;
-- zero registros


select ef.* from service_execution se
join execution_file ef on ef.se_id = se.se_id
where (se.updated_consumed_duration = false and 
		original_values is not null and
		ef.transfer_duration <> 0 and
		ef.transfer_type = 'consumed')
;
-- zero registros


-- backup com os dados pós ajuste usando normalized time de file_metrics
create table execution_file_08_05_2025 as select * from execution_file;

--backup de service executiona com os dados pós ajuste usando normalized time de file_metrics
create table service_execution_08_05_2025 as select * from service_execution;


select distinct se.we_id 
from service_execution se
join execution_file ef on ef.se_id = se.se_id
where (se.updated_consumed_duration = true and
		se.activity_id = 3 and
		ef.transfer_duration <> 0 and
		ef.transfer_type = 'consumed')
; --645.820 registros atualizados por essa query


--update para setar transfer_duration para zero novamente
update execution_file set transfer_duration = 0
where ef_id in (
	select ef.ef_id 
	from service_execution se
	join execution_file ef on ef.se_id = se.se_id
	where   se.updated_consumed_duration = true and
			se.activity_id = 3 and
			ef.transfer_duration <> 0 and
			ef.transfer_type = 'consumed' and
			se.we_id in (68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,
						 135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,
						 201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256
						)
	)
;


--update para retornar os valores originais de duration, billed duration e consumed_files_duration,
-- assim como os campos marcadores
update service_execution se set
duration = t.original_duration,
updated_duration = FALSE,
billed_duration = t.original_billed_duration,
updated_billed_duration = FALSE,
consumed_files_transfer_duration = t.original_consumed_files_transfer_duration,
updated_consumed_duration = FALSE
from 
(		select se.se_id, se.we_id, se.duration, 
			(se.original_values::jsonb->>'duration')::numeric as original_duration, 
			se.billed_duration, 
			(se.original_values::jsonb->>'billed_duration')::numeric as original_billed_duration,
			se.consumed_files_transfer_duration,
			(se.original_values::jsonb->>'consumed_files_transfer_duration')::numeric as original_consumed_files_transfer_duration,
			se.original_values
		from service_execution se
		join provider_configuration pc on pc.conf_id = se.provider_conf_id
		where updated_consumed_duration is TRUE and
			  pc.provider_id = 1 and
			  se.original_values is not null
) t
where se.se_id = t.se_id
;
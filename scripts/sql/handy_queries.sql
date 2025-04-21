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
FROM vw_service_execution_detail
ORDER BY we_id;



--execução em vm: wetag_1744507705125
--WETAG = []

--tentando obter vm_cpu_time
WITH vm_base_time AS (
	SELECT DISTINCT 
		se.se_id, 
		se.we_id,
		we.execution_tag,
		pc.provider_id,
		pr.provider_tag,
		ta.task_id,
		se.activity_id,
		st.statistics_id,
		st.statistics_name, 
		es.value_float as vm_cpu_time
	FROM service_execution se
	JOIN provider_configuration pc on pc.conf_id = se.provider_conf_id
	JOIN provider pr on pr.provider_id = pc.provider_id
	JOIN workflow_execution we ON we.we_id = se.we_id
	JOIN vw_service_execution_task sxt ON sxt.se_id = se.se_id
	JOIN vw_task ta ON ta.task_id = sxt.task_id
	JOIN execution_statistics es ON es.se_id = se.se_id
	JOIN statistics st ON st.statistics_id = es.statistics_id
	WHERE we.execution_tag IN ('wetag_1744507705125') 
		 AND pr.provider_tag = 'aws_ec2'
		 AND st.statistics_name IN ('tree_duration', 'subtree_duration', 'maf_db_creator_duration', 'maf_db_aggregator_duration')
 )
SELECT DISTINCT 
	ta.task_id,
	ta.activity_id,
	ta.task_type,
	vm.vm_cpu_time,
	ta.input_count AS n_input,
	'[' || ta.input_list || ']' AS input_list,
	ta.output_count AS n_output,
	'[' || ta.output_list || ']' AS output_list
FROM service_execution se
JOIN workflow_execution we ON se.we_id = we.we_id
JOIN vw_service_execution_task st ON se.se_id = st.se_id
JOIN vw_task ta ON st.task_id = ta.task_id
JOIN vm_base_time vm ON ta.task_id = vm.task_id
WHERE we.execution_tag in ('wetag_1743638228939')
ORDER BY ta.activity_id, ta.task_id;


--statistics
SELECT DISTINCT 
sei.se_id, sei.we_id, sei.workflow_input_count, sei.execution_tag,  sei.provider_id, sei.provider_name, ta.task_id, sei.activity_id, sei.activity_name, 
stat.statistics_id, stat.statistics_name, 
substr(ta.consumed_files_list,1,30) in_files, 
substr(ta.produced_files_list,1,30) out_files, 
concat(es.value_float, es.value_integer, substr(es.value_string, 1, 100)) as value
FROM vw_service_execution_info sei
LEFT OUTER JOIN vw_service_execution_task st ON sei.se_id = st.se_id
LEFT OUTER JOIN vw_task ta ON st.task_id = ta.task_id
LEFT OUTER JOIN execution_statistics es ON es.se_id = sei.se_id
LEFT OUTER JOIN "statistics" stat ON stat.statistics_id = es.statistics_id
WHERE execution_tag in ('wetag_1744914790201')
ORDER BY ta.task_id, sei.provider_id;



--files
SELECT sei.execution_tag, COUNT(*) as total_files, COUNT(*) * 5 as total_files_for_all_configs, COUNT(*) * 5 / 1000 * 0.007 * 5.90 as estimated_cost
FROM execution_file ef
JOIN vw_service_execution_info sei on sei.se_id = ef.se_id
WHERE execution_tag in ('wetag_1744754708329', 'wetag_1744757716148')
GROUP BY sei.execution_tag;


--tasks
SELECT DISTINCT 
	we.we_id, 
	we.execution_tag, 
	we.input_count, 
	COUNT(*) as n_tasks
FROM vw_task ta 
LEFT OUTER JOIN vw_service_execution_task st ON st.task_id = ta.task_id
LEFT OUTER JOIN service_execution se ON se.se_id = st.se_id
LEFT OUTER JOIN workflow_execution we ON we.we_id = se.we_id
WHERE we.we_id >= 68
GROUP BY we.execution_tag, we.input_count, we.we_id 
;


select
se.se_id, se.we_id, we.execution_tag, p.provider_name, pc.memory_mb, se.activity_id, f.file_id, f.file_name, f.file_size, ef.transfer_type, ef.transfer_duration
from service_execution se
join workflow_execution we on se.we_id = we.we_id
join provider_configuration pc on pc.conf_id = se.provider_conf_id
join provider p on p.provider_id = pc.provider_id
join execution_file ef on ef.se_id = se.se_id
join file f on f.file_id = ef.file_id
where we.we_id = 66
order by f.file_id
;

-- registros com transfer_duration de subtree_files na atividade maf_db_creator = 0
-- executados em fx com cache local desses arquivos para agilizar o processo
-- ajustar pegando o tempo de file_metrics
select
se.se_id, se.we_id, we.execution_tag, p.provider_name, se.activity_id, 
f.file_id, f.file_name, f.file_size, ef.transfer_type, ef.transfer_duration, 
fm.file_name, fm.metric_type, avg(fm.duration_ms) duration_ms, avg(fm.normalized_duration_ms) normalized_duration_ms
from service_execution se
join workflow_execution we on se.we_id = we.we_id
join provider_configuration pc on pc.conf_id = se.provider_conf_id
join provider p on p.provider_id = pc.provider_id
join execution_file ef on ef.se_id = se.se_id
join file f on f.file_id = ef.file_id
left outer join file_metrics fm 
    on f.file_name = fm.file_name 
    and fm.metric_type = CASE 
        WHEN ef.transfer_type = 'consumed' THEN 'download'
        WHEN ef.transfer_type = 'produced' THEN 'upload'
    END
where 
	ef.transfer_duration = 0
	and p.provider_id = 1
group by se.se_id, se.we_id, we.execution_tag, p.provider_name, se.activity_id, 
f.file_id, f.file_name, f.file_size, ef.transfer_type, ef.transfer_duration, 
fm.file_name, fm.metric_type
order by se.we_id;
--263285


-- Atualizar ef.transfer_duration quando for zero
UPDATE execution_file ef
SET transfer_duration = COALESCE(t1.avg_duration_ms, 0)
FROM (
    SELECT 
        f.file_id,
        f.file_name,
        CASE 
            WHEN fm.metric_type = 'download' THEN 'consumed'
            WHEN fm.metric_type = 'upload' THEN 'produced'
        END AS metric_type,
        AVG(fm.normalized_duration_ms) AS avg_duration_ms
    FROM file_metrics fm
    JOIN file f ON f.file_name = fm.file_name
    GROUP BY f.file_id, f.file_name, fm.metric_type
) t1
WHERE
    ef.file_id = t1.file_id AND
    ef.transfer_type = t1.metric_type AND
    ef.transfer_duration = 0 AND
    EXISTS (
        SELECT 1
        FROM service_execution se
        JOIN provider_configuration pc ON se.provider_conf_id = pc.conf_id
        WHERE se.se_id = ef.se_id AND pc.provider_id = 1
    );

select se.we_id, count(*) from execution_file ef
join service_execution se on ef.se_id = se.se_id
where ef.transfer_duration = 0
group by se.we_id;

--CALL delete_execution_data('wetag_1744925395446');

-- Adding indices based on query patterns
	
-- Optimize joins on service_execution
CREATE INDEX idx_service_execution_se_id ON service_execution (se_id);
CREATE INDEX idx_service_execution_we_id ON service_execution (we_id);

-- Optimize joins on workflow_execution
CREATE INDEX idx_workflow_execution_we_id ON workflow_execution (we_id);

-- Optimize joins on provider_configuration
CREATE INDEX idx_provider_configuration_conf_id ON provider_configuration (conf_id);

-- Optimize joins on provider
CREATE INDEX idx_provider_provider_id ON provider (provider_id);

-- Optimize joins on execution_file
CREATE INDEX idx_execution_file_file_id_transfer_type ON execution_file (file_id, transfer_type);

-- Optimize joins on file
CREATE INDEX idx_file_file_name ON file (file_name);

-- Optimize joins on file_metrics
CREATE INDEX idx_file_metrics_file_name_metric_type ON file_metrics (file_name, metric_type);

-- Optimize filtering on execution_file.transfer_duration
CREATE INDEX idx_execution_file_transfer_duration_zero ON execution_file (transfer_duration) WHERE transfer_duration = 0;


-- workflow executions with provider
select distinct we_id, workflow_start_time, workflow_end_time, workflow_duration, workflow_input_count, provider_tag, provider_memory_mb
from vw_service_execution_detail
order by we_id desc;


-- arquivos de entrada para execução em VM baseados na execução em FX
WITH basic_data AS (
    SELECT DISTINCT input_count, input_list
    FROM workflow_execution we
    WHERE we_id between 201 and 256
    ORDER BY input_count
)
SELECT json_object_agg(
    input_count,
    input_list::json
) AS result
FROM basic_data;
-- =====================================================================
-- QUERIES DE VALIDAÇÃO PARA MIGRAÇÃO DE BANCO DE DADOS
-- Execute estas queries na instância antiga e nova para comparar resultados
-- =====================================================================

-- =====================================================================
-- 1. CONTAGEM DE REGISTROS POR TABELA
-- =====================================================================
SELECT 'provider' as objeto, COUNT(*) as total_registros FROM provider
UNION ALL
SELECT 'provider_configuration', COUNT(*) FROM provider_configuration
UNION ALL
SELECT 'workflow', COUNT(*) FROM workflow
UNION ALL
SELECT 'workflow_activity', COUNT(*) FROM workflow_activity
UNION ALL
SELECT 'workflow_execution', COUNT(*) FROM workflow_execution
UNION ALL
SELECT 'service_execution', COUNT(*) FROM service_execution
UNION ALL
SELECT 'file', COUNT(*) FROM file
UNION ALL
SELECT 'execution_file', COUNT(*) FROM execution_file
UNION ALL
SELECT 'statistics', COUNT(*) FROM statistics
UNION ALL
SELECT 'execution_statistics', COUNT(*) FROM execution_statistics
UNION ALL
SELECT 'vm_configurations', COUNT(*) FROM vm_configurations
UNION ALL
SELECT 'bucket_ranges', COUNT(*) FROM bucket_ranges
ORDER BY objeto;

-- =====================================================================
-- 2. CHECKSUMS DAS TABELAS (usando MD5 dos dados ordenados)
-- =====================================================================
SELECT 'provider' as objeto, MD5(string_agg(provider_id::text || '|' || provider_name || '|' || provider_tag, '' ORDER BY provider_id)) as checksum FROM provider
UNION ALL
SELECT 'provider_configuration', MD5(string_agg(conf_id::text || '|' || provider_id::text || '|' || timeout::text || '|' || cpu::text || '|' || memory_mb::text || '|' || storage_mb::text, '' ORDER BY conf_id)) FROM provider_configuration
UNION ALL
SELECT 'workflow', MD5(string_agg(workflow_id::text || '|' || workflow_name || '|' || COALESCE(workflow_description, ''), '' ORDER BY workflow_id)) FROM workflow
UNION ALL
SELECT 'workflow_activity', MD5(string_agg(activity_id::text || '|' || workflow_id::text || '|' || activity_name || '|' || COALESCE(activity_description, ''), '' ORDER BY activity_id)) FROM workflow_activity
UNION ALL
SELECT 'workflow_execution', MD5(string_agg(we_id::text || '|' || workflow_id::text || '|' || execution_tag || '|' || start_time::text || '|' || end_time::text || '|' || duration::text || '|' || input_count::text || '|' || COALESCE(input_list, '') || '|' || COALESCE(runtime_data, '') || '|' || COALESCE(info, ''), '' ORDER BY we_id)) FROM workflow_execution
UNION ALL
SELECT 'service_execution', MD5(string_agg(se_id::text || '|' || we_id::text || '|' || activity_id::text || '|' || provider_conf_id::text || '|' || request_id || '|' || COALESCE(log_stream_name, '') || '|' || start_time::text || '|' || end_time::text || '|' || duration::text || '|' || COALESCE(billed_duration::text, '') || '|' || COALESCE(init_duration::text, '') || '|' || COALESCE(memory_size::text, '') || '|' || COALESCE(max_memory_used::text, '') || '|' || COALESCE(consumed_files_count::text, '') || '|' || COALESCE(consumed_files_size::text, '') || '|' || COALESCE(consumed_files_transfer_duration::text, '') || '|' || COALESCE(produced_files_count::text, '') || '|' || COALESCE(produced_files_size::text, '') || '|' || COALESCE(produced_files_transfer_duration::text, '') || '|' || COALESCE(error_message, '') || '|' || COALESCE(original_values, '') || '|' || COALESCE(updated_consumed_duration::text, 'false') || '|' || COALESCE(updated_duration::text, 'false') || '|' || COALESCE(updated_billed_duration::text, 'false'), '' ORDER BY se_id)) FROM service_execution
UNION ALL
SELECT 'file', MD5(string_agg(file_id::text || '|' || file_name || '|' || COALESCE(file_bucket, '') || '|' || COALESCE(file_path, '') || '|' || file_size::text || '|' || COALESCE(file_hash_code, ''), '' ORDER BY file_id)) FROM file
UNION ALL
SELECT 'execution_file', MD5(string_agg(ef_id::text || '|' || se_id::text || '|' || file_id::text || '|' || transfer_duration::text || '|' || transfer_type, '' ORDER BY ef_id)) FROM execution_file
UNION ALL
SELECT 'statistics', MD5(string_agg(statistics_id::text || '|' || statistics_name || '|' || statistics_description, '' ORDER BY statistics_id)) FROM statistics
UNION ALL
SELECT 'execution_statistics', MD5(string_agg(es_id::text || '|' || se_id::text || '|' || statistics_id::text || '|' || COALESCE(value_float::text, '') || '|' || COALESCE(value_integer::text, '') || '|' || COALESCE(value_string, ''), '' ORDER BY es_id)) FROM execution_statistics
UNION ALL
SELECT 'vm_configurations', MD5(string_agg(vm_id::text || '|' || vm_type || '|' || vcpu::text || '|' || cpu_slowdown::text || '|' || cost::text || '|' || storage::text || '|' || bandwidth::text, '' ORDER BY vm_id)) FROM vm_configurations
UNION ALL
SELECT 'bucket_ranges', MD5(string_agg(bucket_range_id::text || '|' || size1_gb::text || '|' || size2_gb::text || '|' || cost_per_gb::text, '' ORDER BY bucket_range_id)) FROM bucket_ranges
ORDER BY objeto;

-- =====================================================================
-- 3. VALIDAÇÃO DE INTEGRIDADE REFERENCIAL
-- =====================================================================
SELECT 'provider_configuration_fk' as objeto, COUNT(*) as registros_com_problema FROM provider_configuration pc LEFT JOIN provider p ON pc.provider_id = p.provider_id WHERE p.provider_id IS NULL
UNION ALL
SELECT 'workflow_activity_fk', COUNT(*) FROM workflow_activity wa LEFT JOIN workflow w ON wa.workflow_id = w.workflow_id WHERE w.workflow_id IS NULL
UNION ALL
SELECT 'workflow_execution_fk', COUNT(*) FROM workflow_execution we LEFT JOIN workflow w ON we.workflow_id = w.workflow_id WHERE w.workflow_id IS NULL
UNION ALL
SELECT 'service_execution_activity_fk', COUNT(*) FROM service_execution se LEFT JOIN workflow_activity wa ON se.activity_id = wa.activity_id WHERE wa.activity_id IS NULL
UNION ALL
SELECT 'service_execution_workflow_fk', COUNT(*) FROM service_execution se LEFT JOIN workflow_execution we ON se.we_id = we.we_id WHERE we.we_id IS NULL
UNION ALL
SELECT 'service_execution_provider_fk', COUNT(*) FROM service_execution se LEFT JOIN provider_configuration pc ON se.provider_conf_id = pc.conf_id WHERE pc.conf_id IS NULL
UNION ALL
SELECT 'execution_file_se_fk', COUNT(*) FROM execution_file ef LEFT JOIN service_execution se ON ef.se_id = se.se_id WHERE se.se_id IS NULL
UNION ALL
SELECT 'execution_file_file_fk', COUNT(*) FROM execution_file ef LEFT JOIN file f ON ef.file_id = f.file_id WHERE f.file_id IS NULL
UNION ALL
SELECT 'execution_statistics_se_fk', COUNT(*) FROM execution_statistics es LEFT JOIN service_execution se ON es.se_id = se.se_id WHERE se.se_id IS NULL
UNION ALL
SELECT 'execution_statistics_stats_fk', COUNT(*) FROM execution_statistics es LEFT JOIN statistics s ON es.statistics_id = s.statistics_id WHERE s.statistics_id IS NULL
ORDER BY objeto;

-- =====================================================================
-- 4. VALIDAÇÃO DE CONSTRAINTS E REGRAS DE NEGÓCIO
-- =====================================================================
SELECT 'execution_file_transfer_type_check' as objeto, COUNT(*) as registros_com_problema FROM execution_file WHERE transfer_type NOT IN ('consumed', 'produced')
UNION ALL
SELECT 'workflow_execution_duration_check', COUNT(*) FROM workflow_execution WHERE duration < 0
UNION ALL
SELECT 'service_execution_duration_check', COUNT(*) FROM service_execution WHERE duration < 0
UNION ALL
SELECT 'workflow_execution_time_order_check', COUNT(*) FROM workflow_execution WHERE start_time >= end_time
UNION ALL
SELECT 'service_execution_time_order_check', COUNT(*) FROM service_execution WHERE start_time >= end_time
UNION ALL
SELECT 'file_size_check', COUNT(*) FROM file WHERE file_size < 0
ORDER BY objeto;

-- =====================================================================
-- 5. ESTATÍSTICAS AGREGADAS PARA COMPARAÇÃO
-- =====================================================================
SELECT 'execucoes_por_workflow' as objeto,
       'workflow_name=' || COALESCE(w.workflow_name,'') || ';total_execucoes=' || COUNT(we.we_id) || ';primeira_execucao=' || MIN(we.start_time) || ';ultima_execucao=' || MAX(we.end_time) || ';duracao_media=' || AVG(we.duration) || ';total_inputs=' || SUM(we.input_count) as info
FROM workflow w LEFT JOIN workflow_execution we ON w.workflow_id = we.workflow_id
GROUP BY w.workflow_id, w.workflow_name
UNION ALL
SELECT 'service_executions_por_activity',
       'activity_name=' || COALESCE(wa.activity_name,'') || ';total_service_executions=' || COUNT(se.se_id) || ';duracao_media=' || AVG(se.duration) || ';media_files_consumidos=' || AVG(se.consumed_files_count) || ';media_files_produzidos=' || AVG(se.produced_files_count) || ';total_erros=' || COUNT(CASE WHEN se.error_message IS NOT NULL THEN 1 END)
FROM workflow_activity wa LEFT JOIN service_execution se ON wa.activity_id = se.activity_id
GROUP BY wa.activity_id, wa.activity_name
UNION ALL
SELECT 'estatisticas_arquivos',
       'total_arquivos=' || COUNT(*) || ';arquivos_unicos_por_nome=' || COUNT(DISTINCT file_name) || ';tamanho_medio=' || AVG(file_size) || ';menor_arquivo=' || MIN(file_size) || ';maior_arquivo=' || MAX(file_size) || ';tamanho_total=' || SUM(file_size)
FROM file
UNION ALL
SELECT 'estatisticas_transfer_duration',
       'transfer_type=' || transfer_type || ';total_transfers=' || COUNT(*) || ';duracao_media=' || AVG(transfer_duration) || ';menor_duracao=' || MIN(transfer_duration) || ';maior_duracao=' || MAX(transfer_duration) || ';duracao_total=' || SUM(transfer_duration)
FROM execution_file
GROUP BY transfer_type
ORDER BY objeto, info;

-- =====================================================================
-- 6. VERIFICAÇÕES DE SEQUÊNCIAS (SERIAL)
-- =====================================================================
SELECT 'sequence_check' as objeto, schemaname, sequencename, last_value, increment_by, max_value, min_value FROM pg_sequences WHERE schemaname = 'public' ORDER BY sequencename;

-- =====================================================================
-- 7. SAMPLE DE DADOS PARA VERIFICAÇÃO MANUAL
-- =====================================================================
WITH sample_workflow_executions AS (
    SELECT 'sample_workflow_executions' as objeto,
           'we_id=' || we_id || ';execution_tag=' || execution_tag || ';start_time=' || start_time || ';duration=' || duration as info
    FROM workflow_execution
    ORDER BY we_id LIMIT 50
),
sample_service_executions AS (
    SELECT 'sample_service_executions' as objeto,
           'se_id=' || se_id || ';request_id=' || request_id || ';start_time=' || start_time || ';duration=' || duration || ';error_message=' || COALESCE(error_message,'') as info
    FROM service_execution
    ORDER BY se_id LIMIT 50
),
sample_files AS (
    SELECT 'sample_files' as objeto,
           'file_id=' || file_id || ';file_name=' || file_name || ';file_size=' || file_size || ';file_hash_code=' || COALESCE(file_hash_code,'') as info
    FROM file
    ORDER BY file_id LIMIT 50
)
SELECT * FROM sample_workflow_executions
UNION ALL
SELECT * FROM sample_service_executions
UNION ALL
SELECT * FROM sample_files;

-- =====================================================================
-- INSTRUÇÕES DE USO:
-- 
-- 1. Execute este script completo na instância ANTIGA
-- 2. Salve os resultados em um arquivo
-- 3. Execute este script completo na instância NOVA
-- 4. Compare os resultados linha por linha
-- 
-- Os resultados devem ser IDÊNTICOS entre as duas instâncias se a 
-- migração foi bem-sucedida.
-- =====================================================================

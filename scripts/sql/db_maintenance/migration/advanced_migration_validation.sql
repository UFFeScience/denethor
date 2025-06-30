-- =====================================================================
-- QUERIES AVANÇADAS DE VALIDAÇÃO PÓS-MIGRAÇÃO
-- Execute após as queries básicas para validações mais específicas
-- =====================================================================

-- =====================================================================
-- 1. VALIDAÇÃO DE DADOS ÚNICOS E DUPLICATAS
-- =====================================================================

-- Verificar se há duplicatas na tabela workflow_execution (execution_tag deve ser único)
SELECT 'duplicata_execution_tag' as validacao,
       execution_tag,
       COUNT(*) as ocorrencias
FROM workflow_execution
GROUP BY execution_tag
HAVING COUNT(*) > 1;

-- Verificar se há duplicatas na tabela file (combinação de campos deve ser única)
SELECT 'duplicata_file_unique_constraint' as validacao,
       file_name,
       file_bucket,
       file_path,
       file_size,
       COUNT(*) as ocorrencias
FROM file
GROUP BY file_name, file_bucket, file_path, file_size
HAVING COUNT(*) > 1;

-- Verificar se há duplicatas na tabela task (combinação de activity_id, input_list, output_list deve ser única)
SELECT 'duplicata_task_unique_constraint' as validacao,
       activity_id,
       input_list,
       output_list,
       COUNT(*) as ocorrencias
FROM task
GROUP BY activity_id, input_list, output_list
HAVING COUNT(*) > 1;

-- =====================================================================
-- 2. VALIDAÇÃO DE CONSISTÊNCIA DE DADOS CALCULADOS
-- =====================================================================

-- Verificar se a duração calculada bate com start_time e end_time em workflow_execution
SELECT 'workflow_execution_duration_consistency' as validacao,
       we_id,
       duration as duration_stored,
       EXTRACT(EPOCH FROM (end_time - start_time)) as duration_calculated,
       ABS(duration - EXTRACT(EPOCH FROM (end_time - start_time))) as diferenca
FROM workflow_execution
WHERE ABS(duration - EXTRACT(EPOCH FROM (end_time - start_time))) > 0.001
ORDER BY diferenca DESC
LIMIT 10;

-- Verificar se a duração calculada bate com start_time e end_time em service_execution
SELECT 'service_execution_duration_consistency' as validacao,
       se_id,
       duration as duration_stored,
       EXTRACT(EPOCH FROM (end_time - start_time)) as duration_calculated,
       ABS(duration - EXTRACT(EPOCH FROM (end_time - start_time))) as diferenca
FROM service_execution
WHERE ABS(duration - EXTRACT(EPOCH FROM (end_time - start_time))) > 0.001
ORDER BY diferenca DESC
LIMIT 10;

-- =====================================================================
-- 3. VALIDAÇÃO DE RANGES E VALORES EXTREMOS
-- =====================================================================

-- Verificar se há valores extremos ou suspeitos em durações
SELECT 'workflow_execution_extreme_durations' as validacao,
       MIN(duration) as min_duration,
       MAX(duration) as max_duration,
       AVG(duration) as avg_duration,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration) as p95_duration,
       COUNT(CASE WHEN duration > 86400 THEN 1 END) as durations_over_24h,
       COUNT(CASE WHEN duration = 0 THEN 1 END) as zero_durations
FROM workflow_execution;

SELECT 'service_execution_extreme_durations' as validacao,
       MIN(duration) as min_duration,
       MAX(duration) as max_duration,
       AVG(duration) as avg_duration,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration) as p95_duration,
       COUNT(CASE WHEN duration > 86400 THEN 1 END) as durations_over_24h,
       COUNT(CASE WHEN duration = 0 THEN 1 END) as zero_durations
FROM service_execution;

-- Verificar valores extremos em file_size
SELECT 'file_extreme_sizes' as validacao,
       MIN(file_size) as min_size,
       MAX(file_size) as max_size,
       AVG(file_size) as avg_size,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY file_size) as p95_size,
       COUNT(CASE WHEN file_size > 1073741824 THEN 1 END) as files_over_1gb,
       COUNT(CASE WHEN file_size = 0 THEN 1 END) as zero_size_files
FROM file;

-- =====================================================================
-- 4. VALIDAÇÃO DE CONSISTÊNCIA ENTRE TABELAS RELACIONADAS
-- =====================================================================

-- Verificar se consumed_files_count e produced_files_count em service_execution
-- batem com os registros em execution_file
SELECT 'service_execution_file_count_consistency' as validacao,
       se.se_id,
       se.consumed_files_count as consumed_stored,
       se.produced_files_count as produced_stored,
       COUNT(CASE WHEN ef.transfer_type = 'consumed' THEN 1 END) as consumed_actual,
       COUNT(CASE WHEN ef.transfer_type = 'produced' THEN 1 END) as produced_actual,
       ABS(COALESCE(se.consumed_files_count, 0) - COUNT(CASE WHEN ef.transfer_type = 'consumed' THEN 1 END)) as consumed_diff,
       ABS(COALESCE(se.produced_files_count, 0) - COUNT(CASE WHEN ef.transfer_type = 'produced' THEN 1 END)) as produced_diff
FROM service_execution se
LEFT JOIN execution_file ef ON se.se_id = ef.se_id
GROUP BY se.se_id, se.consumed_files_count, se.produced_files_count
HAVING ABS(COALESCE(se.consumed_files_count, 0) - COUNT(CASE WHEN ef.transfer_type = 'consumed' THEN 1 END)) > 0
    OR ABS(COALESCE(se.produced_files_count, 0) - COUNT(CASE WHEN ef.transfer_type = 'produced' THEN 1 END)) > 0
ORDER BY consumed_diff + produced_diff DESC
LIMIT 10;

-- Verificar se input_count em workflow_execution bate com alguma lógica de contagem
SELECT 'workflow_execution_input_consistency' as validacao,
       we.we_id,
       we.input_count as input_count_stored,
       CASE 
           WHEN we.input_list IS NOT NULL AND we.input_list != '' 
           THEN array_length(string_to_array(we.input_list, ','), 1)
           ELSE 0 
       END as input_count_calculated,
       ABS(we.input_count - CASE 
           WHEN we.input_list IS NOT NULL AND we.input_list != '' 
           THEN array_length(string_to_array(we.input_list, ','), 1)
           ELSE 0 
       END) as diferenca
FROM workflow_execution we
WHERE ABS(we.input_count - CASE 
           WHEN we.input_list IS NOT NULL AND we.input_list != '' 
           THEN array_length(string_to_array(we.input_list, ','), 1)
           ELSE 0 
       END) > 0
ORDER BY diferenca DESC
LIMIT 10;

-- =====================================================================
-- 5. VALIDAÇÃO DE TIMESTAMPS E ORDENAÇÃO TEMPORAL
-- =====================================================================

-- Verificar se há service_executions que começaram antes do workflow_execution
SELECT 'temporal_consistency_se_we' as validacao,
       se.se_id,
       se.start_time as se_start,
       we.start_time as we_start,
       se.end_time as se_end,
       we.end_time as we_end
FROM service_execution se
JOIN workflow_execution we ON se.we_id = we.we_id
WHERE se.start_time < we.start_time 
   OR se.end_time > we.end_time
ORDER BY se.se_id
LIMIT 10;

-- Verificar se há timestamps no futuro
SELECT 'future_timestamps' as validacao,
       'workflow_execution' as tabela,
       COUNT(*) as registros_futuros
FROM workflow_execution
WHERE start_time > NOW() OR end_time > NOW()
UNION ALL
SELECT 'future_timestamps' as validacao,
       'service_execution' as tabela,
       COUNT(*) as registros_futuros
FROM service_execution
WHERE start_time > NOW() OR end_time > NOW();

-- =====================================================================
-- 6. VALIDAÇÃO DE ENCODING E CARACTERES ESPECIAIS
-- =====================================================================

-- Verificar se há caracteres não-UTF8 ou problemas de encoding
SELECT 'encoding_issues' as validacao,
       'workflow' as tabela,
       COUNT(*) as registros_com_problema
FROM workflow
WHERE workflow_name != convert_from(convert_to(workflow_name, 'UTF8'), 'UTF8')
   OR (workflow_description IS NOT NULL AND workflow_description != convert_from(convert_to(workflow_description, 'UTF8'), 'UTF8'));

SELECT 'encoding_issues' as validacao,
       'file' as tabela,
       COUNT(*) as registros_com_problema
FROM file
WHERE file_name != convert_from(convert_to(file_name, 'UTF8'), 'UTF8');

-- =====================================================================
-- 7. ANÁLISE DE COMPLETUDE DOS DADOS
-- =====================================================================

-- Verificar percentual de campos nulos em campos opcionais importantes
SELECT 'data_completeness' as analise,
       'service_execution' as tabela,
       COUNT(*) as total_registros,
       COUNT(log_stream_name) as log_stream_preenchido,
       ROUND(COUNT(log_stream_name) * 100.0 / COUNT(*), 2) as pct_log_stream,
       COUNT(billed_duration) as billed_duration_preenchido,
       ROUND(COUNT(billed_duration) * 100.0 / COUNT(*), 2) as pct_billed_duration,
       COUNT(init_duration) as init_duration_preenchido,
       ROUND(COUNT(init_duration) * 100.0 / COUNT(*), 2) as pct_init_duration,
       COUNT(error_message) as error_message_preenchido,
       ROUND(COUNT(error_message) * 100.0 / COUNT(*), 2) as pct_error_message
FROM service_execution;

SELECT 'data_completeness' as analise,
       'file' as tabela,
       COUNT(*) as total_registros,
       COUNT(file_bucket) as file_bucket_preenchido,
       ROUND(COUNT(file_bucket) * 100.0 / COUNT(*), 2) as pct_file_bucket,
       COUNT(file_path) as file_path_preenchido,
       ROUND(COUNT(file_path) * 100.0 / COUNT(*), 2) as pct_file_path,
       COUNT(file_hash_code) as file_hash_code_preenchido,
       ROUND(COUNT(file_hash_code) * 100.0 / COUNT(*), 2) as pct_file_hash_code
FROM file;

-- =====================================================================
-- 8. VALIDAÇÃO DE PERFORMANCE (ÍNDICES)
-- =====================================================================

-- Verificar se todos os índices esperados existem
SELECT 'index_validation' as validacao,
       schemaname,
       tablename,
       indexname,
       indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- =====================================================================
-- 9. QUERIES DE STRESS TEST PARA PERFORMANCE
-- =====================================================================

-- Query que usa vários índices - deve ter performance similar em ambas as instâncias
EXPLAIN (ANALYZE, BUFFERS)
SELECT se.se_id, se.duration, we.execution_tag, wa.activity_name, f.file_name
FROM service_execution se
JOIN workflow_execution we ON se.we_id = we.we_id
JOIN workflow_activity wa ON se.activity_id = wa.activity_id
JOIN execution_file ef ON se.se_id = ef.se_id
JOIN file f ON ef.file_id = f.file_id
WHERE se.start_time >= '2023-01-01'
  AND ef.transfer_type = 'consumed'
  AND se.duration > 10
ORDER BY se.start_time DESC
LIMIT 100;

-- =====================================================================
-- INSTRUÇÕES ADICIONAIS:
-- 
-- 1. Execute estas queries após as queries básicas
-- 2. Foque especialmente nos resultados que mostram inconsistências
-- 3. Se alguma validação retorna registros, investigue mais profundamente
-- 4. As queries de EXPLAIN devem ter planos similares (mas não idênticos)
-- =====================================================================

-- =====================================================================
-- QUERIES DE INVESTIGAÇÃO E TROUBLESHOOTING PÓS-MIGRAÇÃO
-- Use estas queries para investigar problemas específicos encontrados
-- =====================================================================

-- =====================================================================
-- 1. INVESTIGAÇÃO DE DIFERENÇAS EM CHECKSUMS
-- =====================================================================

-- Se os checksums das tabelas não baterem, use estas queries para investigar

-- Comparar registros específicos da tabela service_execution (exemplo)
-- Substitua os IDs pelos que apresentaram diferenças
SELECT se_id, we_id, activity_id, provider_conf_id, request_id, 
       start_time, end_time, duration, error_message,
       updated_consumed_duration, updated_duration, updated_billed_duration
FROM service_execution 
WHERE se_id IN (1, 2, 3, 4, 5)  -- Substitua pelos IDs problemáticos
ORDER BY se_id;

-- Verificar diferenças em timestamps (podem ter precisão diferente)
SELECT se_id,
       start_time,
       EXTRACT(MICROSECONDS FROM start_time) as start_microseconds,
       end_time,
       EXTRACT(MICROSECONDS FROM end_time) as end_microseconds
FROM service_execution
WHERE se_id IN (1, 2, 3, 4, 5)  -- Substitua pelos IDs problemáticos
ORDER BY se_id;

-- =====================================================================
-- 2. INVESTIGAÇÃO DE SEQUÊNCIAS
-- =====================================================================

-- Verificar o estado atual das sequências
SELECT 
    c.relname as sequence_name,
    c.relnamespace::regnamespace as schema_name,
    CASE 
        WHEN c.relkind = 'S' THEN 
            (SELECT last_value FROM pg_sequences WHERE sequencename = c.relname AND schemaname = c.relnamespace::regnamespace::text)
        ELSE NULL 
    END as last_value
FROM pg_class c
WHERE c.relkind = 'S'
AND c.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
ORDER BY c.relname;

-- Verificar se as sequências estão sincronizadas com os dados
SELECT 'provider' as tabela,
       MAX(provider_id) as max_id,
       (SELECT last_value FROM pg_sequences WHERE sequencename = 'provider_provider_id_seq') as sequence_value,
       (SELECT last_value FROM pg_sequences WHERE sequencename = 'provider_provider_id_seq') - MAX(provider_id) as diferenca
FROM provider
UNION ALL
SELECT 'workflow_execution' as tabela,
       MAX(we_id) as max_id,
       (SELECT last_value FROM pg_sequences WHERE sequencename = 'workflow_execution_we_id_seq') as sequence_value,
       (SELECT last_value FROM pg_sequences WHERE sequencename = 'workflow_execution_we_id_seq') - MAX(we_id) as diferenca
FROM workflow_execution
UNION ALL
SELECT 'service_execution' as tabela,
       MAX(se_id) as max_id,
       (SELECT last_value FROM pg_sequences WHERE sequencename = 'service_execution_se_id_seq') as sequence_value,
       (SELECT last_value FROM pg_sequences WHERE sequencename = 'service_execution_se_id_seq') - MAX(se_id) as diferenca
FROM service_execution;

-- =====================================================================
-- 3. INVESTIGAÇÃO DE PERFORMANCE
-- =====================================================================

-- Verificar tamanho das tabelas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Verificar estatísticas das tabelas
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;

-- =====================================================================
-- 4. VERIFICAÇÃO DE CONSTRAINTS E ÍNDICES
-- =====================================================================

-- Verificar se todas as constraints foram migradas
SELECT 
    tc.constraint_name,
    tc.table_name,
    tc.constraint_type,
    kcu.column_name,
    rc.match_option,
    rc.update_rule,
    rc.delete_rule,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu
    ON tc.constraint_catalog = kcu.constraint_catalog
    AND tc.constraint_schema = kcu.constraint_schema
    AND tc.constraint_name = kcu.constraint_name
LEFT JOIN information_schema.referential_constraints rc
    ON tc.constraint_catalog = rc.constraint_catalog
    AND tc.constraint_schema = rc.constraint_schema
    AND tc.constraint_name = rc.constraint_name
LEFT JOIN information_schema.constraint_column_usage ccu
    ON rc.unique_constraint_catalog = ccu.constraint_catalog
    AND rc.unique_constraint_schema = ccu.constraint_schema
    AND rc.unique_constraint_name = ccu.constraint_name
WHERE tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

-- Verificar se todos os índices foram criados
SELECT 
    i.relname as index_name,
    t.relname as table_name,
    a.attname as column_name,
    am.amname as index_type,
    ix.indisunique as is_unique,
    ix.indisprimary as is_primary
FROM pg_class i
JOIN pg_index ix ON i.oid = ix.indexrelid
JOIN pg_class t ON ix.indrelid = t.oid
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
JOIN pg_am am ON i.relam = am.oid
WHERE t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
AND t.relkind = 'r'
ORDER BY t.relname, i.relname;

-- =====================================================================
-- 5. QUERIES PARA DEBUGGING DE DADOS ESPECÍFICOS
-- =====================================================================

-- Encontrar workflow_executions órfãs (sem service_executions)
SELECT we.we_id, we.execution_tag, we.start_time
FROM workflow_execution we
LEFT JOIN service_execution se ON we.we_id = se.we_id
WHERE se.we_id IS NULL
ORDER BY we.start_time DESC
LIMIT 10;

-- Encontrar service_executions órfãs (sem execution_files)
SELECT se.se_id, se.request_id, se.start_time
FROM service_execution se
LEFT JOIN execution_file ef ON se.se_id = ef.se_id
WHERE ef.se_id IS NULL
ORDER BY se.start_time DESC
LIMIT 10;

-- Encontrar arquivos órfãos (sem execution_files)
SELECT f.file_id, f.file_name, f.file_size
FROM file f
LEFT JOIN execution_file ef ON f.file_id = ef.file_id
WHERE ef.file_id IS NULL
ORDER BY f.file_size DESC
LIMIT 10;

-- =====================================================================
-- 6. ANÁLISE DE DADOS SUSPEITOS
-- =====================================================================

-- Service executions com duração muito alta ou muito baixa
SELECT se_id, request_id, duration, start_time, end_time, error_message
FROM service_execution
WHERE duration > 3600  -- Mais de 1 hora
   OR duration < 0.001  -- Menos de 1ms
ORDER BY duration DESC
LIMIT 20;

-- Arquivos com tamanhos suspeitos
SELECT file_id, file_name, file_size, file_bucket, file_path
FROM file
WHERE file_size > 10737418240  -- Maior que 10GB
   OR file_size = 0  -- Tamanho zero
ORDER BY file_size DESC
LIMIT 20;

-- Execuções com contagens inconsistentes
SELECT se_id, consumed_files_count, produced_files_count, 
       consumed_files_size, produced_files_size,
       consumed_files_transfer_duration, produced_files_transfer_duration
FROM service_execution
WHERE (consumed_files_count > 0 AND consumed_files_size = 0)
   OR (produced_files_count > 0 AND produced_files_size = 0)
   OR (consumed_files_count = 0 AND consumed_files_size > 0)
   OR (produced_files_count = 0 AND produced_files_size > 0)
ORDER BY se_id
LIMIT 20;

-- =====================================================================
-- 7. QUERIES PARA RECONCILIAÇÃO MANUAL
-- =====================================================================

-- Comparar contagens por data (útil para identificar períodos problemáticos)
SELECT 
    DATE(start_time) as execution_date,
    COUNT(*) as total_executions,
    COUNT(DISTINCT we_id) as distinct_workflows,
    AVG(duration) as avg_duration,
    SUM(CASE WHEN error_message IS NOT NULL THEN 1 ELSE 0 END) as error_count
FROM service_execution
GROUP BY DATE(start_time)
ORDER BY execution_date DESC
LIMIT 30;

-- Hash de subconjuntos dos dados para identificar onde estão as diferenças
SELECT 
    'first_1000_service_executions' as subset,
    MD5(string_agg(se_id::text || '|' || request_id || '|' || duration::text, '' ORDER BY se_id)) as hash
FROM (
    SELECT se_id, request_id, duration
    FROM service_execution
    ORDER BY se_id
    LIMIT 1000
) t
UNION ALL
SELECT 
    'last_1000_service_executions' as subset,
    MD5(string_agg(se_id::text || '|' || request_id || '|' || duration::text, '' ORDER BY se_id)) as hash
FROM (
    SELECT se_id, request_id, duration
    FROM service_execution
    ORDER BY se_id DESC
    LIMIT 1000
) t;

-- =====================================================================
-- 8. COMANDOS ÚTEIS PARA INVESTIGAÇÃO
-- =====================================================================

-- Para executar no psql para análise detalhada:
-- \dt+ - Lista todas as tabelas com tamanhos
-- \di+ - Lista todos os índices com tamanhos
-- \d+ nome_tabela - Mostra estrutura detalhada da tabela
-- \timing on - Habilita medição de tempo das queries

-- Para verificar configurações do PostgreSQL:
-- SHOW ALL;
-- SELECT name, setting, unit, context FROM pg_settings WHERE name IN ('shared_buffers', 'work_mem', 'maintenance_work_mem');

-- =====================================================================
-- INSTRUÇÕES DE USO:
-- 
-- 1. Use estas queries quando encontrar diferenças na validação básica
-- 2. Execute as queries relevantes baseado no tipo de problema encontrado
-- 3. Compare os resultados entre as duas instâncias
-- 4. Use os resultados para identificar a causa raiz dos problemas
-- =====================================================================

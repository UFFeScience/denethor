-- Identificar outliers para downloads
-- Um outlier é definido como um registro cujo tempo de duração está a mais de 2 desvios padrão da média.
-- A consulta calcula a média e o desvio padrão para cada arquivo e tipo de métrica, 
-- e seleciona registros que estão fora do intervalo [média - 2*desvio padrão, média + 2*desvio padrão].
WITH stats AS (
    SELECT 
        file_name,
        metric_type,
        COUNT(*) AS observation_count, -- Número de observações
        AVG(duration_ms) AS avg_duration,
        STDDEV(duration_ms) AS stddev_duration
    FROM file_metrics
    WHERE metric_type = 'download'
    GROUP BY file_name, metric_type
)
SELECT 
    fm.file_name,
    fm.metric_type,
    fm.duration_ms,
    s.observation_count, -- Número de observações
    s.avg_duration,
    s.stddev_duration
FROM file_metrics fm
JOIN stats s
    ON fm.file_name = s.file_name AND fm.metric_type = s.metric_type
WHERE fm.metric_type = 'download'
  AND (fm.duration_ms > s.avg_duration + 2 * s.stddev_duration 
       OR fm.duration_ms < s.avg_duration - 2 * s.stddev_duration)
ORDER BY fm.file_name, fm.duration_ms;

-- Identificar outliers para uploads
-- A lógica é a mesma da consulta anterior, mas aplicada ao tipo de métrica 'upload'.
WITH stats AS (
    SELECT 
        file_name,
        metric_type,
        COUNT(*) AS observation_count, -- Número de observações
        AVG(duration_ms) AS avg_duration,
        STDDEV(duration_ms) AS stddev_duration
    FROM file_metrics
    WHERE metric_type = 'upload'
    GROUP BY file_name, metric_type
)
SELECT 
    fm.file_name,
    fm.metric_type,
    fm.duration_ms,
    s.observation_count, -- Número de observações
    s.avg_duration,
    s.stddev_duration
FROM file_metrics fm
JOIN stats s
    ON fm.file_name = s.file_name AND fm.metric_type = s.metric_type
WHERE fm.metric_type = 'upload'
  AND (fm.duration_ms > s.avg_duration + 2 * s.stddev_duration 
       OR fm.duration_ms < s.avg_duration - 2 * s.stddev_duration)
ORDER BY fm.file_name, fm.duration_ms;

-- Identificar outliers com base na taxa de transferência (file_size / duration_ms)
-- Um outlier é definido como um registro cuja taxa de transferência está a mais de 2 desvios padrão da média.
WITH stats AS (
    SELECT 
        file_name,
        metric_type,
        COUNT(*) AS observation_count, -- Número de observações
        AVG(file_size / duration_ms) AS avg_transfer_rate, -- Média da taxa de transferência
        STDDEV(file_size / duration_ms) AS stddev_transfer_rate -- Desvio padrão da taxa de transferência
    FROM file_metrics
    GROUP BY file_name, metric_type
)
SELECT 
    fm.file_name,
    fm.metric_type,
    fm.file_size,
    fm.duration_ms,
    (fm.file_size / fm.duration_ms) AS transfer_rate, -- Taxa de transferência do registro
    s.observation_count, -- Número de observações
    s.avg_transfer_rate, -- Média da taxa de transferência
    s.stddev_transfer_rate -- Desvio padrão da taxa de transferência
FROM file_metrics fm
JOIN stats s
    ON fm.file_name = s.file_name AND fm.metric_type = s.metric_type
WHERE (fm.file_size / fm.duration_ms) > s.avg_transfer_rate + 2 * s.stddev_transfer_rate 
   OR (fm.file_size / fm.duration_ms) < s.avg_transfer_rate - 2 * s.stddev_transfer_rate
ORDER BY fm.file_name, transfer_rate;


-- Criar faixas de tamanho de arquivo
-- As faixas foram definidas com base na distribuição fornecida.
WITH file_with_size_ranges AS (
    SELECT 
        file_name,
        metric_type,
        file_size,
        duration_ms,
        (file_size / duration_ms) AS file_transfer_rate, -- Taxa de transferência do registro
        CASE 
            WHEN file_size <= 500 THEN '0-500'
            WHEN file_size <= 1000 THEN '501-1000'
            WHEN file_size <= 2000 THEN '1001-2000'
            WHEN file_size <= 3000 THEN '2001-3000'
            WHEN file_size <= 4000 THEN '3001-4000'
            WHEN file_size <= 5000 THEN '4001-5000'
            ELSE '5001+'
        END AS size_range
    FROM file_metrics
),
stats AS (
    -- Calcular média e desvio padrão da taxa de transferência por faixa de tamanho
    SELECT 
        size_range,
        metric_type,
        COUNT(*) AS observation_count, -- Número de observações
        MAX(file_transfer_rate) AS max_transfer_rate, -- Max da taxa de transferência
        MIN(file_transfer_rate) AS min_transfer_rate, -- Min da taxa de transferência
        AVG(file_transfer_rate) AS avg_transfer_rate, -- Média da taxa de transferência
        STDDEV(file_transfer_rate) AS stddev_transfer_rate -- Desvio padrão da taxa de transferência
    FROM file_with_size_ranges
    GROUP BY size_range, metric_type
)
-- Identificar outliers com base na taxa de transferência dentro de cada faixa de tamanho
SELECT 
    fsr.file_name,
    fsr.metric_type,
    fsr.file_size,
    fsr.size_range,
    fsr.duration_ms,
    fsr.file_transfer_rate,
    s.observation_count,
    s.max_transfer_rate,
    s.min_transfer_rate,
    s.avg_transfer_rate,
    s.stddev_transfer_rate
FROM file_with_size_ranges fsr
JOIN stats s ON fsr.size_range = s.size_range AND fsr.metric_type = s.metric_type
WHERE fsr.file_transfer_rate > (s.avg_transfer_rate + 2 * s.stddev_transfer_rate)
    OR fsr.file_transfer_rate < (s.avg_transfer_rate - 2 * s.stddev_transfer_rate)
ORDER BY fsr.size_range, fsr.file_transfer_rate;



-- 1. **Cálculo dos Percentis**:
--    - A CTE `percentiles` calcula o 5º e o 95º percentil da taxa de transferência (`file_transfer_rate`) para cada faixa de tamanho (`size_range`) e tipo de métrica (`metric_type`).

-- 2. **Identificação de Outliers**:
--    - A query principal seleciona registros cuja taxa de transferência está abaixo do 5º percentil ou acima do 95º percentil, indicando valores extremos.

-- 3. **Vantagem dos Percentis**:
--    - Percentis são mais robustos contra distribuições não normais e outliers extremos, tornando-os úteis para identificar anomalias em dados com alta variabilidade.

-- Identificar outliers com base na taxa de transferência usando percentis (5º e 95º)
WITH file_with_size_ranges AS (
    SELECT 
        file_name,
        metric_type,
        file_size,
        duration_ms,
        (file_size / duration_ms) AS file_transfer_rate, -- Taxa de transferência do registro
        CASE 
            WHEN file_size <= 500 THEN '0-500'
            WHEN file_size <= 1000 THEN '501-1000'
            WHEN file_size <= 2000 THEN '1001-2000'
            WHEN file_size <= 3000 THEN '2001-3000'
            WHEN file_size <= 4000 THEN '3001-4000'
            WHEN file_size <= 5000 THEN '4001-5000'
            ELSE '5001+'
        END AS size_range
    FROM file_metrics
),
percentiles AS (
    -- Calcular os percentis 5 e 95 para a taxa de transferência por faixa de tamanho
    SELECT 
        size_range,
        metric_type,
        COUNT(*) AS observation_count, -- Número de observações
        MAX(file_transfer_rate) AS max_transfer_rate, -- Max da taxa de transferência
        MIN(file_transfer_rate) AS min_transfer_rate, -- Min da taxa de transferência
        AVG(file_transfer_rate) AS avg_transfer_rate, -- Média da taxa de transferência
        PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY file_transfer_rate) AS p5_transfer_rate, -- 5º percentil
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY file_transfer_rate) AS p95_transfer_rate -- 95º percentil
    FROM file_with_size_ranges fsr
    GROUP BY size_range, metric_type
)
-- Identificar outliers com base nos percentis
SELECT 
    fsr.file_name,
    fsr.metric_type,
    fsr.file_size,
    fsr.size_range,
    fsr.duration_ms,
    fsr.file_transfer_rate,
    p.observation_count,
    p.max_transfer_rate,
    p.min_transfer_rate,
    p.avg_transfer_rate,
    p.p5_transfer_rate, -- 5º percentil
    p.p95_transfer_rate, -- 95º percentil
    CASE 
		WHEN fsr.file_transfer_rate < p.p5_transfer_rate THEN p.p5_transfer_rate - fsr.file_transfer_rate
		WHEN fsr.file_transfer_rate > p.p95_transfer_rate THEN fsr.file_transfer_rate - p.p95_transfer_rate
		ELSE 0
	END AS deviation_from_percentile
FROM file_with_size_ranges fsr
JOIN percentiles p ON fsr.size_range = p.size_range AND fsr.metric_type = p.metric_type
WHERE fsr.file_transfer_rate < p.p5_transfer_rate -- Abaixo do 5º percentil
   OR fsr.file_transfer_rate > p.p95_transfer_rate -- Acima do 95º percentil
ORDER BY deviation_from_percentile DESC, fsr.size_range, fsr.file_transfer_rate;
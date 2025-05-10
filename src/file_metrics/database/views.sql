DROP VIEW IF EXISTS vw_file_metrics_transfer_rate;

CREATE OR REPLACE VIEW vw_file_metrics_transfer_rate AS (
    WITH file_size_range AS (
    SELECT 
        id,
		metric_type,
        CASE 
            WHEN file_size <= 100 THEN '0000-0100'
            WHEN file_size <= 200 THEN '0101-0200'
            WHEN file_size <= 300 THEN '0201-0300'
            WHEN file_size <= 400 THEN '0301-0400'
            WHEN file_size <= 500 THEN '0401-0500'
            WHEN file_size <= 1000 THEN '0501-1000'
            WHEN file_size <= 2500 THEN '1001-2500'
            WHEN file_size <= 5000 THEN '2501-5000'
            ELSE '5001+'
            END AS size_range,
        (file_size / duration_ms) AS file_transfer_rate -- Taxa de transferência do registro
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
        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY file_transfer_rate) p50_transfer_rate, -- Mediana da taxa de transferência
        PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY file_transfer_rate) AS p5_transfer_rate, -- 5º percentil
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY file_transfer_rate) AS p95_transfer_rate, -- 95º percentil
		STDDEV(file_transfer_rate) AS stddev_transfer_rate -- Desvio padrão da taxa de transferência
    FROM file_size_range fsr
    GROUP BY size_range, metric_type
    )
    SELECT 
        fm.*,
        CASE
            WHEN fm.metric_type = 'download' THEN 'consumed'
            WHEN fm.metric_type = 'upload' THEN 'produced'
        END AS transfer_type,
		fsr.file_transfer_rate,
        p.size_range,
		p.observation_count,
		p.max_transfer_rate,
		p.min_transfer_rate,
		p.avg_transfer_rate,
		p.p50_transfer_rate,
		p.p5_transfer_rate,
		p.p95_transfer_rate,
        p.stddev_transfer_rate,
        CASE 
            WHEN fsr.file_transfer_rate < p.p5_transfer_rate THEN p.p5_transfer_rate - fsr.file_transfer_rate
            WHEN fsr.file_transfer_rate > p.p95_transfer_rate THEN fsr.file_transfer_rate - p.p95_transfer_rate
            ELSE 0
        END AS deviation_from_percentile,
        CASE 
            WHEN fsr.file_transfer_rate < p.p5_transfer_rate THEN 'ABAIXO_DO_5_PERC'
            WHEN fsr.file_transfer_rate > p.p95_transfer_rate THEN 'ACIMA_DO_95_PERC'
            ELSE 'OK'
        END AS status
    FROM file_metrics fm
	JOIN file_size_range fsr on fsr.id = fm.id
    JOIN percentiles p ON fsr.size_range = p.size_range AND fsr.metric_type = p.metric_type
    ORDER BY fm.metric_type, fsr.size_range, fsr.file_transfer_rate
)
;







DROP VIEW IF EXISTS vw_file_metrics_transfer_duration;

CREATE OR REPLACE VIEW vw_file_metrics_transfer_duration AS (
    WITH file_size_range AS (
    SELECT 
        id,
		metric_type,
        CASE 
            WHEN file_size <= 100 THEN '0000-0100'
            WHEN file_size <= 200 THEN '0101-0200'
            WHEN file_size <= 300 THEN '0201-0300'
            WHEN file_size <= 400 THEN '0301-0400'
            WHEN file_size <= 500 THEN '0401-0500'
            WHEN file_size <= 1000 THEN '0501-1000'
            WHEN file_size <= 2500 THEN '1001-2500'
            WHEN file_size <= 5000 THEN '2501-5000'
            ELSE '5001+'
            END AS size_range,
        duration_ms AS file_transfer_duration
	FROM file_metrics
	),
    percentiles AS (
    -- Calcular os percentis 5 e 95 para a taxa de transferência por faixa de tamanho
    SELECT 
        size_range,
        metric_type,
        COUNT(*) AS observation_count, -- Número de observações
        MAX(file_transfer_duration) AS max_transfer_duration, -- Max da duração da transferência
        MIN(file_transfer_duration) AS min_transfer_duration, -- Min da duração da transferência
        AVG(file_transfer_duration) AS avg_transfer_duration, -- Média da duração da transferência
        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY file_transfer_duration) p50_transfer_duration, -- Mediana da duração da transferência
        PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY file_transfer_duration) AS p5_transfer_duration, -- 5º percentil
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY file_transfer_duration) AS p95_transfer_duration, -- 95º percentil
		STDDEV(file_transfer_duration) AS stddev_transfer_duration -- Desvio padrão da duração da transferência
    FROM file_size_range fsr
    GROUP BY size_range, metric_type
    )
    SELECT 
        fm.*,
        CASE
            WHEN fm.metric_type = 'download' THEN 'consumed'
            WHEN fm.metric_type = 'upload' THEN 'produced'
        END AS transfer_type,
		fsr.file_transfer_duration,
        p.size_range,
		p.observation_count,
		p.max_transfer_duration,
		p.min_transfer_duration,
		p.avg_transfer_duration,
		p.p50_transfer_duration,
		p.p5_transfer_duration,
		p.p95_transfer_duration,
        p.stddev_transfer_duration,
        CASE 
            WHEN fsr.file_transfer_duration < p.p5_transfer_duration THEN p.p5_transfer_duration - fsr.file_transfer_duration
            WHEN fsr.file_transfer_duration > p.p95_transfer_duration THEN fsr.file_transfer_duration - p.p95_transfer_duration
            ELSE 0
        END AS deviation_from_percentile,
        CASE 
            WHEN fsr.file_transfer_duration < p.p5_transfer_duration THEN 'ABAIXO_DO_5_PERC'
            WHEN fsr.file_transfer_duration > p.p95_transfer_duration THEN 'ACIMA_DO_95_PERC'
            ELSE 'OK'
        END AS status
    FROM file_metrics fm
	JOIN file_size_range fsr on fsr.id = fm.id
    JOIN percentiles p ON fsr.size_range = p.size_range AND fsr.metric_type = p.metric_type
    ORDER BY fm.metric_type, fsr.size_range, fsr.file_transfer_duration
)
;
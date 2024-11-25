--#<bucket_range_id> <size1_gb> <size2_gb> <cost_per_gb>
SELECT 1 AS bucket_range_id, 0 AS size1_gb, 50*1024 AS size2_gb, 0.0405 AS cost_per_gb
UNION ALL
SELECT 2 AS bucket_range_id, 50*1024 AS size1_gb, 450*1024 AS size2_gb, 0.039 AS cost_per_gb
UNION ALL
SELECT 3 AS bucket_range_id, 450*1024 AS size1_gb, 99999999999999 AS size2_gb, 0.037 AS cost_per_gb

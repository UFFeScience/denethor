--#<bucket_range_id> <size1_gb> <size2_gb> <cost_per_gb>
SELECT 
    bucket_range_id,
    size1_gb::numeric * 1024 * 1024 * 1024 AS size1_bytes,
    size2_gb::numeric * 1024 * 1024 * 1024 AS size2_bytes,
    cost_per_gb::numeric / (1024 * 1024 * 1024) AS cost_per_byte
FROM bucket_ranges
ORDER BY bucket_range_id;
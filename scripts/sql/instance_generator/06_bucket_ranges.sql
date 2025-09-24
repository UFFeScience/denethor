--#<bucket_range_id> <size1_bytes> <size2_bytes> <cost_per_byte>
SELECT 
    bucket_range_id,
    to_char(size1_gb::numeric * 1024 * 1024 * 1024, 'fm9999999999999999999999999999') AS size1_bytes,
    to_char(size2_gb::numeric * 1024 * 1024 * 1024, 'fm9999999999999999999999999999') AS size2_bytes,
    to_char(cost_per_gb::numeric / (1024 * 1024 * 1024), 'fm999990D9999999999999999999999999999') AS cost_per_byte
FROM bucket_ranges
ORDER BY bucket_range_id;
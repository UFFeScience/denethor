--#<vm_id> <cpu_slowdown> <cost_per_second> <storage_mb> <bandwidth_mbps>
SELECT 
    vm_id,
    cpu_slowdown,
    cost::numeric / 1000.0 AS cost_per_ms,
    storage::numeric * 1024 * 1024 AS storage_bytes,
    bandwidth AS bandwidth_mbps
FROM vm_configurations
ORDER BY vm_id
;
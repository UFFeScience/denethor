--#<vm_id> <cpu_slowdown> <cost_per_second> <storage_bytes> <bandwidth_mbps>
SELECT 
    vm_id,
    cpu_slowdown,
    cost AS cost_per_second,
    to_char(storage::numeric * 1024 * 1024,  'fm9999999999999999999999999999') AS storage_bytes,
    bandwidth AS bandwidth_mbps
FROM vm_configurations
ORDER BY vm_id
;
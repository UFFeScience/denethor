--#<vm_id> <cpu_slowdown> <cost_per_second> <storage_mb> <bandwidth_mbps>
SELECT 
    vm_id,
    cpu_slowdown,
    cost AS cost_per_second,
    storage AS storage_mb,
    bandwidth AS bandwidth_mbps
FROM vm_configurations
ORDER BY vm_id
;
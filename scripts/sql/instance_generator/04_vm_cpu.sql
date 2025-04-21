--#<vm1_cpu_slowdown> <vm2_cpu_slowdown> ... <vm10_cpu_slowdown>
SELECT 
    MAX(CASE WHEN vm_id = 1 THEN cpu_slowdown END) AS vm1_cpu_slowdown,
    MAX(CASE WHEN vm_id = 2 THEN cpu_slowdown END) AS vm2_cpu_slowdown,
    MAX(CASE WHEN vm_id = 3 THEN cpu_slowdown END) AS vm3_cpu_slowdown
FROM vm_configurations;
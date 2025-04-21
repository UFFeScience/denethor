--#<vm1_cpu_slowdown> <vm2_cpu_slowdown> ... <vm10_cpu_slowdown>
SELECT 
    MAX(CASE WHEN vm_id = 1 THEN cpu_slowdown END) AS vm1_cpu_slowdown,
    MAX(CASE WHEN vm_id = 2 THEN cpu_slowdown END) AS vm2_cpu_slowdown,
    MAX(CASE WHEN vm_id = 3 THEN cpu_slowdown END) AS vm3_cpu_slowdown--,
    MAX(CASE WHEN vm_id = 4 THEN cpu_slowdown END) AS vm4_cpu_slowdown,
    MAX(CASE WHEN vm_id = 5 THEN cpu_slowdown END) AS vm5_cpu_slowdown,
    MAX(CASE WHEN vm_id = 6 THEN cpu_slowdown END) AS vm6_cpu_slowdown,
    MAX(CASE WHEN vm_id = 7 THEN cpu_slowdown END) AS vm7_cpu_slowdown,
    MAX(CASE WHEN vm_id = 8 THEN cpu_slowdown END) AS vm8_cpu_slowdown,
    MAX(CASE WHEN vm_id = 9 THEN cpu_slowdown END) AS vm9_cpu_slowdown
FROM vm_configurations;
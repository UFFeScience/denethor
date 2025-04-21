--#<vm1_cost> <vm2_cost> <vm3_cost>
SELECT 
    MAX(CASE WHEN vm_id = 1 THEN cost END) AS vm1_cost,
    MAX(CASE WHEN vm_id = 2 THEN cost END) AS vm2_cost,
    MAX(CASE WHEN vm_id = 3 THEN cost END) AS vm3_cost--,
    MAX(CASE WHEN vm_id = 4 THEN cost END) AS vm4_cost,
    MAX(CASE WHEN vm_id = 5 THEN cost END) AS vm5_cost,
    MAX(CASE WHEN vm_id = 6 THEN cost END) AS vm6_cost,
    MAX(CASE WHEN vm_id = 7 THEN cost END) AS vm7_cost,
    MAX(CASE WHEN vm_id = 8 THEN cost END) AS vm8_cost,
    MAX(CASE WHEN vm_id = 9 THEN cost END) AS vm9_cost
FROM vm_configurations;
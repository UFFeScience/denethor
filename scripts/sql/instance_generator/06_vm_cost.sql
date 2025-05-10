--#<vm1_cost> <vm2_cost> <vm3_cost>
SELECT 
    MAX(CASE WHEN vm_id = 1 THEN cost END) AS vm1_cost,
    MAX(CASE WHEN vm_id = 2 THEN cost END) AS vm2_cost,
    MAX(CASE WHEN vm_id = 3 THEN cost END) AS vm3_cost,
    MAX(CASE WHEN vm_id = 4 THEN cost END) AS vm4_cost,
    MAX(CASE WHEN vm_id = 5 THEN cost END) AS vm5_cost
FROM (SELECT * FROM vm_configurations ORDER BY vm_id)
;
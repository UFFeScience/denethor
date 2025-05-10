--#<vm1_storage> <vm2 _storage> <vm3_storage>
SELECT 
    MAX(CASE WHEN vm_id = 1 THEN storage END) AS vm1_storage,
    MAX(CASE WHEN vm_id = 2 THEN storage END) AS vm2_storage,
    MAX(CASE WHEN vm_id = 3 THEN storage END) AS vm3_storage,
    MAX(CASE WHEN vm_id = 3 THEN storage END) AS vm4_storage,
    MAX(CASE WHEN vm_id = 3 THEN storage END) AS vm5_storage
FROM (SELECT * FROM vm_configurations ORDER BY vm_id)
;

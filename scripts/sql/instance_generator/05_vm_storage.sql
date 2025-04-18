--#<vm1_storage> <vm2 _storage> <vm3_storage>
SELECT 
    MAX(CASE WHEN vm_id = 1 THEN storage END) AS vm1_storage,
    MAX(CASE WHEN vm_id = 2 THEN storage END) AS vm2_storage,
    MAX(CASE WHEN vm_id = 3 THEN storage END) AS vm3_storage--,
    -- MAX(CASE WHEN vm_id = 4 THEN storage END) AS vm4_storage,
    -- MAX(CASE WHEN vm_id = 5 THEN storage END) AS vm5_storage,
    -- MAX(CASE WHEN vm_id = 6 THEN storage END) AS vm6_storage,
    -- MAX(CASE WHEN vm_id = 7 THEN storage END) AS vm7_storage,
    -- MAX(CASE WHEN vm_id = 8 THEN storage END) AS vm8_storage,
    -- MAX(CASE WHEN vm_id = 9 THEN storage END) AS vm9_storage
FROM vm_configurations;
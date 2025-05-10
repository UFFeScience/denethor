--#<vm_id> <bandwidth>
SELECT 
    vm_id,
    bandwidth
FROM (SELECT * FROM vm_configurations ORDER BY vm_id)
;
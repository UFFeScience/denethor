--Q1: What are the produced files by Subtree Mining for input file ORTHOMCL1000?
SELECT f.file_name, f.file_size, f.file_bucket, se.start_time
FROM file f
JOIN execution_file ef ON f.file_id = ef.file_id
JOIN service_execution se ON ef.se_id = se.se_id
WHERE f.file_name LIKE '%ORTHOMCL1000%.nexus'
ORDER BY f.file_name;


--Q2: What is the execution time of Tree Constructor for a specific input file ORTHOMCL1000
SELECT wa.activity_name, f.file_name, se.duration AS execution_time
FROM workflow_activity wa
JOIN service_execution se ON wa.activity_id = se.activity_id
JOIN execution_file ef ON se.se_id = ef.se_id
JOIN file f ON ef.file_id = f.file_id
WHERE wa.activity_name = 'tree_constructor' AND f.file_name = 'ORTHOMCL1000';


--Q3 Retrieve the combinations of function parameters for the last 3 executions of the CSE application.
WITH t_executions AS (
    SELECT wa.activity_id, wa.activity_name, se.provider_id, se.start_time, se.duration activity_duration, 
           ROW_NUMBER() OVER(PARTITION BY wa.activity_name ORDER BY se.start_time DESC) as rn
    FROM workflow_activity wa
    JOIN service_execution se ON wa.activity_id = se.activity_id
)
SELECT te.activity_id, te.activity_name, te.activity_duration, te.start_time,
sp.provider_id, sp.provider_name, sp.provider_ram, sp.provider_timeout, sp.provider_cpu, sp.provider_storage_mb
FROM t_executions te 
JOIN service_provider sp ON sp.provider_id = te.provider_id
WHERE rn <= 5;


--Q4 What is the average execution time of Tree Constructor over the last 3 months?
SELECT wa.activity_name, AVG(se.duration) AS average_execution_time
FROM workflow_activity wa
JOIN service_execution se ON wa.activity_id = se.activity_id
WHERE wa.activity_name = 'tree_constructor' AND se.start_time >= (CURRENT_DATE - INTERVAL '3 months')
GROUP BY wa.activity_name;



--Q5 What is the data derivation path of file ORTHOMCL1000?
WITH t_consumed AS (
    SELECT se.se_id AS execution_id, f.file_name, ef.transfer_type, replace(replace(f.file_name, 'tree_', ''), '.nexus', '') as base_name
    FROM file f
    JOIN execution_file ef ON f.file_id = ef.file_id
    JOIN service_execution se ON ef.se_id = se.se_id
    WHERE f.file_name in ('tree_ORTHOMCL1000.nexus', 'ORTHOMCL1000') and ef.transfer_type = 'consumed'
)
SELECT distinct tc.file_name as consumed_file, f.file_name AS produced_file, wa.activity_name --, se.start_time
FROM t_consumed tc
JOIN execution_file ef ON tc.execution_id = ef.se_id
JOIN file f ON ef.file_id = f.file_id
JOIN service_execution se ON ef.se_id = se.se_id
JOIN workflow_activity wa ON se.activity_id = wa.activity_id
WHERE ef.transfer_type = 'produced' and
      -- to avoid the base_name match with other files that have the name partially equal
      -- ex: "ORTHOMCL1" should not match with "tree_ORTHOMCL1002.nexus" or "tree_ORTHOMCL1002_Inner1.nexus"
      (f.file_name like '%'||tc.base_name||'\_%.nexus' or f.file_name like '%'||tc.base_name||'.nexus%')
ORDER BY consumed_file, produced_file;
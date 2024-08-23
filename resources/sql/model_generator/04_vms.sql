--<vm1_cpu_slowdown> <vm2_cpu_slowdown> ... <vm*_cpu_slowdown>
--<vm1_storage> <vm2_storage> ... <vm* _storage>
--<vm1_cost> <vm2_cost> ... <vm*_cost>
SELECT 1 AS vm1_cpu_slowdown, 0.8 AS vm2_cpu_slowdown, 0.75 AS vm3_cpu_slowdown
UNION ALL
SELECT 10000 AS vm1_storage, 10000 AS vm2_storage, 10000 AS vm3_storage
UNION ALL
SELECT 1 AS vm1_cost, 1.3 AS vm2_cost, 1.5 AS vm3_cost;
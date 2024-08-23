--Totais
--<#tasks> <#config> <#data> <#devices> <#periods> <#buckets> <#ranges> <max_financial_cost>
SELECT 
	(SELECT count(*) AS _tasks FROM service_execution se WHERE se.workflow_execution_id = 'weid_1724184708846'),
	(SELECT count(*) AS _config FROM provider_configuration),
	(SELECT count(*) AS _data FROM file),
	(SELECT 3 AS _devices),
	(SELECT 1 AS _periods),
	(SELECT 1 AS _buckets),
	(SELECT 2 AS _ranges),
	(SELECT 100000 AS _max_financial_cost)
;



-- SELECT * FROM vw_service_execution_info_last;
-- SELECT * FROM provider_configuration;
-- SELECT * FROM workflow_activity;
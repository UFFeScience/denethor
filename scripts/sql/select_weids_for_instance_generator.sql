-- seleção de dados para geração de instâncias
-- run_1__first_n_files_002_to_050: we_id between 68 and 134
-- run_2__random_n_files_002_to_050: we_id between 135 and 200

SELECT DISTINCT 
        provider_id, 
        provider_tag, 
		ARRAY_AGG(DISTINCT we_id ORDER BY we_id) weids
FROM vw_service_execution_detail
-- WHERE we_id between 135 and 189 or we_id between 190 and 200
WHERE we_id between 201 and 256 or we_id between 257 and 267
GROUP BY provider_id, provider_tag
ORDER BY provider_id
;

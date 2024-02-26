-- service_execution
SET lc_numeric = 'pt_BR';
select se.id as se_id, 
		sp.name as servide_provider, 
		wo.name as workflow, 
		wa.name as activity, 
        se.request_id, 
		se.start_time, 
		se.end_time, 
		to_char(se.duration,'fm9999999D99') as duration,
		to_char(se.billed_duration,'fm9999999D99') as billed_duration,
		to_char(se.init_duration,'fm9999999D99') as init_duration,
		se.memory_size, se.max_memory_used, 
		se.consumed_files_count,
		se.consumed_files_size, 
		to_char(se.consumed_files_transfer_duration,'fm9999999D99') consumed_files_transfer_duration,
		se.produced_files_count, 
		se.produced_files_size,
		to_char(se.produced_files_transfer_duration,'fm9999999D99') produced_files_transfer_duration
from service_execution se
join workflow_activity wa on wa.id = se.activity_id
join workflow wo on wo.id = wa.workflow_id
join service_provider sp on sp.id = se.provider_id
order by se.id asc;



-- files
SET lc_numeric = 'pt_BR';
select se.id as se_id,
		sp.name as servide_provider,
		wo.name as workflow,
		wa.name as activity,
		fi.id as file_id,
		fi.name as file_name,
		fi.size as file_size,
		fi.path as file_path,
		fi.bucket,
		to_char(ef.transfer_duration,'fm9999999D99') as transfer_duration,
		ef.transfer_type
from service_execution se
join workflow_activity wa on wa.id = se.activity_id
join workflow wo on wo.id = wa.workflow_id
join service_provider sp on sp.id = se.provider_id
join execution_file ef on ef.se_id = se.id
join file fi on fi.id = ef.file_id
where fi.name like '%ORTHOMCL1000%'
order by se.id asc, fi.id asc;

-- statistics
SET lc_numeric = 'pt_BR';
select se.id as se_id,
		sp.name as servide_provider,
		wo.name as workflow,
		wa.name as activity,
		st.name as statistics_name,
		COALESCE(to_char(es.value_float,'fm9999999D99'),
				 to_char(es.value_integer,'fm9999999D99'),
				 es.value_string) as value
from service_execution se
join workflow_activity wa on wa.id = se.activity_id
join workflow wo on wo.id = wa.workflow_id
join service_provider sp on sp.id = se.provider_id
join execution_statistics es on es.se_id = se.id
join statistics st on st.id = es.statistics_id
order by se.id, st.id;



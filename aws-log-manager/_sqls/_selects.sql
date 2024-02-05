-- service_execution
SET lc_numeric = 'pt_BR';
select se.id as service_execution_id, sp.name as servide_provider, w.name as workflow, wa.name as activity, 
        se.request_id, se.start_time, se.end_time, 
		to_char(se.duration,'fm9999999D99') as duration,
		to_char(se.billed_duration,'fm9999999D99') as billed_duration,
		to_char(se.init_duration,'fm9999999D99') as init_duration,
		se.memory_size, se.max_memory_used, 
		se.consumed_files_count, se.produced_files_count, 
		se.consumed_files_size, se.produced_files_size,
		to_char(se.consumed_files_transfer_duration,'fm9999999D99') consumed_files_transfer_duration,
		to_char(se.produced_files_transfer_duration,'fm9999999D99') produced_files_transfer_duration
from service_execution se
join workflow_activity wa on se.activity_id = wa.id
join workflow w on wa.workflow_id = w.id
join service_provider sp on se.service_id = sp.id
order by se.id asc;



-- files
SET lc_numeric = 'pt_BR';
select se.id as service_execution_id, sp.name as servide_provider, w.name as workflow, wa.name as activity,
		f.id as file_id, f.name as file_name, f.size, f.path, f.bucket,
		to_char(ef.transfer_duration,'fm9999999D99') as transfer_duration, ef.transfer_type
from service_execution se
join workflow_activity wa on se.activity_id = wa.id
join workflow w on wa.workflow_id = w.id
join service_provider sp on se.service_id = sp.id
join execution_file ef on se.id = ef.service_execution_id
join file f on ef.file_id = f.id
order by se.id asc, f.id asc;

-- statistics
SET lc_numeric = 'pt_BR';
select se.id as service_execution_id, sp.name as servide_provider, w.name as workflow, wa.name as activity,
		es.service_execution_id, s.name as statistics_name,
		COALESCE(to_char(es.value_float,'fm9999999D99'),
				 to_char(es.value_integer,'fm9999999D99'),
				 es.value_string) as value
from service_execution se
join workflow_activity wa on se.activity_id = wa.id
join workflow w on wa.workflow_id = w.id
join service_provider sp on se.service_id = sp.id
join execution_statistics es on es.service_execution_id = se.id
join statistics s on es.statistics_id = s.id
order by se.id, s.id;



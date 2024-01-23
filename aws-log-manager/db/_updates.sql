-- Ajustes dos registro de log do tree_constructor para o novo modelo (com n arquivos para uma execução)
-- O tree_constructor só gera um arquivo, mas seus logs não trazem as informações abaixo
-- Os updates a seguir compilam esses dados a partir de execution_files e file

update service_execution se set num_consumed_files = (
	select count(*) 
	from execution_files ef
	where ef.service_execution_id = se.id and ef.action_type = 'consumed'
);

update service_execution se set num_produced_files = (
	select count(*) 
	from execution_files ef
	where ef.service_execution_id = se.id and ef.action_type = 'produced'
);

update service_execution se set total_consumed_transfer_duration = (
	select sum(ef.transfer_duration) 
	from execution_files ef
	where ef.service_execution_id = se.id and ef.action_type = 'consumed'
);

update service_execution se set total_produced_transfer_duration = (
	select sum(ef.transfer_duration) 
	from execution_files ef
	where ef.service_execution_id = se.id and ef.action_type = 'produced'
);

update service_execution se set total_consumed_files_size = (
	select sum(f.size) 
	from execution_files ef
	join file f on ef.file_id = f.id
	where ef.service_execution_id = se.id and ef.action_type = 'consumed'
);

update service_execution se set total_produced_files_size = (
	select sum(f.size) 
	from execution_files ef
	join file f on ef.file_id = f.id
	where ef.service_execution_id = se.id and ef.action_type = 'produced'
);


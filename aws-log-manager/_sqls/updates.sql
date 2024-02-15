-- Ajustes dos registro de log do tree_constructor para o novo modelo (com n arquivos para uma execução)
-- O tree_constructor só gera um arquivo, mas seus logs não trazem as informações abaixo
-- Os updates a seguir compilam esses dados a partir de execution_file e file

update service_execution se set consumed_files_count = (
	select count(*) 
	from execution_file ef
	where ef.service_execution_id = se.id and ef.transfer_type = 'consumed'
);

update service_execution se set produced_files_count = (
	select count(*) 
	from execution_file ef
	where ef.service_execution_id = se.id and ef.transfer_type = 'produced'
);

update service_execution se set consumed_files_transfer_duration = (
	select sum(ef.transfer_duration) 
	from execution_file ef
	where ef.service_execution_id = se.id and ef.transfer_type = 'consumed'
);

update service_execution se set produced_files_transfer_duration = (
	select sum(ef.transfer_duration) 
	from execution_file ef
	where ef.service_execution_id = se.id and ef.transfer_type = 'produced'
);

update service_execution se set consumed_files_size = (
	select sum(f.size) 
	from execution_file ef
	join file f on ef.file_id = f.id
	where ef.service_execution_id = se.id and ef.transfer_type = 'consumed'
);

update service_execution se set produced_files_size = (
	select sum(f.size) 
	from execution_file ef
	join file f on ef.file_id = f.id
	where ef.service_execution_id = se.id and ef.transfer_type = 'produced'
);


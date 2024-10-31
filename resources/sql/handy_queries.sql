select * from vw_service_execution_info_last
order by se_id;

select * from service_execution 
where workflow_execution_id = 'weid_1729872039000';


--DELETE DE REGISTROS DEPENDENTES PARA UM DETERMINADO WORKFLOW_EXECUTION_ID
delete from execution_file where se_id in (
select se_id from service_execution 
where workflow_execution_id = 'weid_1729872039000'
);

delete from execution_statistics where se_id in (
select se_id from service_execution 
where workflow_execution_id = 'weid_1729872039000'
);

delete from "file" where file_id not in (
select file_id from execution_file
);

delete from "statistics" where statistics_id not in (
select statistics_id from execution_statistics
);

delete from service_execution 
where workflow_execution_id = 'weid_1729872039000';
DROP VIEW IF EXISTS vw_file_type;
DROP VIEW IF EXISTS vw_service_execution_info_recent;
DROP VIEW IF EXISTS vw_service_execution_info;
DROP VIEW IF EXISTS vw_task;
DROP VIEW IF EXISTS vw_service_execution_task;


DROP TABLE IF EXISTS public.execution_statistics;
DROP TABLE IF EXISTS public."statistics";
DROP TABLE IF EXISTS public.execution_file;
DROP TABLE IF EXISTS public."file";
DROP TABLE IF EXISTS public.service_execution;
DROP TABLE IF EXISTS public.workflow_execution;
DROP TABLE IF EXISTS public.workflow_activity;
DROP TABLE IF EXISTS public.workflow;
DROP TABLE IF EXISTS public.provider_configuration;
DROP TABLE IF EXISTS public."provider";




CREATE TABLE provider (
    provider_id SERIAL PRIMARY KEY,
    provider_name VARCHAR NOT NULL,
    provider_tag VARCHAR NOT NULL
);

CREATE TABLE provider_configuration (
    conf_id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL,
    timeout INTEGER NOT NULL,
    cpu INTEGER NOT NULL,
    memory_mb INTEGER NOT NULL,
    storage_mb INTEGER NOT NULL,
    FOREIGN KEY (provider_id) REFERENCES provider(provider_id)
);

CREATE TABLE workflow (
    workflow_id SERIAL PRIMARY KEY,
    workflow_name VARCHAR NOT NULL,
    workflow_description VARCHAR
);

CREATE TABLE workflow_activity (
    activity_id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL,
    activity_name VARCHAR NOT NULL,
    activity_description VARCHAR,
    FOREIGN KEY (workflow_id) REFERENCES workflow(workflow_id)
);

CREATE TABLE workflow_execution (
    we_id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL,
    execution_tag VARCHAR NOT NULL UNIQUE,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration FLOAT NOT NULL,
    input_count INTEGER NOT NULL,
    input_list TEXT,
    runtime_data TEXT,
    info TEXT,
    FOREIGN KEY (workflow_id) REFERENCES workflow(workflow_id)
);

CREATE TABLE service_execution (
    se_id SERIAL  PRIMARY KEY,
    we_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    provider_conf_id INTEGER NOT NULL,
    request_id VARCHAR NOT NULL,
    log_stream_name VARCHAR,
    start_ti    me TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration FLOAT NOT NULL,
    billed_duration FLOAT,
    init_duration FLOAT,
    memory_size INTEGER,
    max_memory_used INTEGER,
    consumed_files_count INTEGER,
    consumed_files_size INTEGER,
    consumed_files_transfer_duration FLOAT,
    produced_files_count INTEGER,
    produced_files_size INTEGER,
    produced_files_transfer_duration FLOAT,
    error_message VARCHAR,
    FOREIGN KEY (activity_id) REFERENCES workflow_activity(activity_id),
    FOREIGN KEY (we_id) REFERENCES workflow_execution(we_id),
    FOREIGN KEY (provider_conf_id) REFERENCES provider_configuration(conf_id)
);


CREATE TABLE file (
    file_id SERIAL PRIMARY KEY,
    file_name VARCHAR NOT NULL,
    file_bucket VARCHAR,
    file_path VARCHAR,
    file_size FLOAT NOT NULL,
    file_hash_code VARCHAR NOT NULL,
    UNIQUE (file_name, file_bucket, file_path, file_size)
);

-- Provisoriamente retirando a restrição de NOT NULL para file_hash_code
ALTER TABLE "file" ALTER COLUMN file_hash_code DROP NOT NULL;

CREATE TABLE execution_file (
    ef_id SERIAL  PRIMARY KEY,
    se_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    transfer_duration FLOAT NOT NULL,
    transfer_type VARCHAR NOT NULL,
    CHECK (transfer_type IN ('consumed', 'produced')),
    FOREIGN KEY (se_id) REFERENCES service_execution(se_id),
    FOREIGN KEY (file_id) REFERENCES file(file_id)
);

CREATE TABLE statistics (
    statistics_id SERIAL  PRIMARY KEY,
    statistics_name VARCHAR NOT NULL,
    statistics_description VARCHAR NOT NULL
);

CREATE TABLE execution_statistics (
    es_id SERIAL  PRIMARY KEY,
    se_id INTEGER NOT NULL,
    statistics_id INTEGER NOT NULL,
    value_float FLOAT,
    value_integer INTEGER,
    value_string VARCHAR,
    FOREIGN KEY (se_id) REFERENCES service_execution(se_id),
    FOREIGN KEY (statistics_id) REFERENCES statistics(statistics_id)
);


-- Criação da tabela task
-- CREATE TABLE task (
--     task_id SERIAL PRIMARY KEY,
--     activity_id INTEGER NOT NULL,
--     task_type INTEGER NOT NULL,
--     input_count INTEGER NOT NULL,
--     input_list TEXT NOT NULL,
--     output_count INTEGER NOT NULL,
--     output_list TEXT NOT NULL,
--     FOREIGN KEY (activity_id) REFERENCES workflow_activity(activity_id)
-- );

-- select * from task;





-- INSERT INTO provider_configuration (provider_id, timeout, cpu, memory_mb, storage_mb)
-- VALUES (1, 30, 1, 128, 512);

-- INSERT INTO provider_configuration (provider_id, timeout, cpu, memory_mb, storage_mb)
-- VALUES (1, 45, 1, 256, 512);

-- INSERT INTO provider_configuration (provider_id, timeout, cpu, memory_mb, storage_mb)
-- VALUES (1, 300, 1, 512, 512);

-- INSERT INTO provider_configuration (provider_id, timeout, cpu, memory_mb, storage_mb)
-- VALUES (1, 300, 1, 1024, 512);

-- INSERT INTO provider_configuration (provider_id, timeout, cpu, memory_mb, storage_mb)
-- VALUES (1, 300, 1, 2048, 512);


-- update service_execution se set configuration_id = case 
-- 			when se.activity_id = 1 then 1
-- 			when se.activity_id = 2 then 2
-- 			when se.activity_id = 3 then 3
-- 			when se.activity_id = 4 then 1
-- 		end ;
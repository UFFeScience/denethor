-- DROP TABLE IF EXISTS task;
-- DROP TABLE IF EXISTS execution_statistics;
-- DROP TABLE IF EXISTS execution_file;
-- DROP TABLE IF EXISTS service_execution;
-- DROP TABLE IF EXISTS workflow_activity;
-- DROP TABLE IF EXISTS workflow_execution;
-- DROP TABLE IF EXISTS task;
-- DROP TABLE IF EXISTS file;
-- DROP TABLE IF EXISTS provider_configuration;
-- DROP TABLE IF EXISTS provider;
-- DROP TABLE IF EXISTS workflow;
-- DROP TABLE IF EXISTS statistics;


--DROP COLUMN we_id;
--ALTER TABLE service_execution DROP COLUMN we_id;


CREATE TABLE provider (
    provider_id SERIAL PRIMARY KEY,
    provider_name VARCHAR,
    provider_tag VARCHAR
);

-- TODO: remover provider_id da tabela provider_configuration??
CREATE TABLE provider_configuration (
    configuration_id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES provider(provider_id),
    timeout INTEGER,
    cpu INTEGER,
    memory_mb INTEGER,
    storage_mb INTEGER
);

CREATE TABLE workflow (
    workflow_id SERIAL  PRIMARY KEY,
    workflow_name VARCHAR,
    workflow_description VARCHAR
);

CREATE TABLE workflow_activity (
    activity_id SERIAL  PRIMARY KEY,
    workflow_id INTEGER,
    activity_name VARCHAR,
    activity_description VARCHAR,
    CONSTRAINT fk_workflow_activity_workflow FOREIGN KEY (workflow_id) REFERENCES workflow(workflow_id)
);

CREATE TABLE workflow_execution (
    we_id SERIAL  PRIMARY KEY,
    we_tag VARCHAR,
    workflow_id INTEGER,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    duration FLOAT,
    input_count INTEGER,
    task_count INTEGER,
    service_execution_count INTEGER,
    input_list TEXT,
    runtime_data TEXT,
    info TEXT,
    CONSTRAINT fk_workflow_execution_workflow FOREIGN KEY (workflow_id) REFERENCES workflow(workflow_id)
);

CREATE TABLE service_execution (
    se_id SERIAL  PRIMARY KEY,
    we_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    provider_id INTEGER NOT NULL,
    configuration_id INTEGER,
    workflow_execution_id VARCHAR, --sera movido para workflow_execution como we_tag
    request_id VARCHAR,
    log_stream_name VARCHAR,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    duration FLOAT,
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
    CONSTRAINT fk_service_execution_workflow_execution FOREIGN KEY (we_id) REFERENCES workflow_execution(we_id),
    CONSTRAINT fk_service_execution_provider FOREIGN KEY (provider_id) REFERENCES provider(provider_id),
    CONSTRAINT fk_service_execution_configuration FOREIGN KEY (configuration_id) REFERENCES provider_configuration(configuration_id),
    CONSTRAINT fk_service_execution_activity FOREIGN KEY (activity_id) REFERENCES workflow_activity(activity_id)
);

ALTER TABLE service_execution
ADD COLUMN we_id INTEGER NOT NULL,
ADD CONSTRAINT fk_service_execution_workflow_execution FOREIGN KEY (we_id) REFERENCES workflow_execution(we_id);


CREATE TABLE file (
    file_id SERIAL PRIMARY KEY,
    file_name VARCHAR NOT NULL,
    file_bucket VARCHAR,
    file_path VARCHAR,
    file_size FLOAT NOT NULL,
    file_hash_code VARCHAR NOT NULL,
    CONSTRAINT uk_file_data UNIQUE (file_name, file_bucket, file_path, file_size)
);

CREATE TABLE execution_file (
    ef_id SERIAL  PRIMARY KEY,
    se_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    transfer_duration FLOAT,
    transfer_type VARCHAR NOT NULL CONSTRAINT check_action_type CHECK (transfer_type IN ('consumed', 'produced')),
    CONSTRAINT fk_execution_file_service_execution FOREIGN KEY (se_id) REFERENCES service_execution(se_id),
    CONSTRAINT fk_execution_file_file FOREIGN KEY (file_id) REFERENCES file(file_id)
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
    CONSTRAINT fk_execution_statistics_service_execution FOREIGN KEY (se_id) REFERENCES service_execution(se_id),
    CONSTRAINT fk_execution_statistics_statistics FOREIGN KEY (statistics_id) REFERENCES statistics(statistics_id)
);


-- Criação da tabela task
CREATE TABLE task (
    task_id SERIAL PRIMARY KEY,
    activity_id INTEGER NOT NULL,
    task_type INTEGER NOT NULL,
    input_count INTEGER NOT NULL,
    input_list TEXT NOT NULL,
    output_count INTEGER NOT NULL,
    output_list TEXT NOT NULL,
    FOREIGN KEY (activity_id) REFERENCES workflow_activity(activity_id)
);

select * from task;





INSERT INTO provider_configuration (provider_id, timeout, cpu, memory_mb, storage_mb)
VALUES (1, 30, 1, 128, 512);

INSERT INTO provider_configuration (provider_id, timeout, cpu, memory_mb, storage_mb)
VALUES (1, 45, 1, 256, 512);

INSERT INTO provider_configuration (provider_id, timeout, cpu, memory_mb, storage_mb)
VALUES (1, 300, 1, 512, 512);

INSERT INTO provider_configuration (provider_id, timeout, cpu, memory_mb, storage_mb)
VALUES (1, 300, 1, 1024, 512);

INSERT INTO provider_configuration (provider_id, timeout, cpu, memory_mb, storage_mb)
VALUES (1, 300, 1, 2048, 512);


update service_execution se set configuration_id = case 
			when se.activity_id = 1 then 1
			when se.activity_id = 2 then 2
			when se.activity_id = 3 then 3
			when se.activity_id = 4 then 1
		end ;
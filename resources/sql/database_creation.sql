DROP TABLE IF EXISTS task_file;
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS execution_statistics;
DROP TABLE IF EXISTS execution_file;
DROP TABLE IF EXISTS service_execution;
DROP TABLE IF EXISTS workflow_activity;
DROP TABLE IF EXISTS file;
DROP TABLE IF EXISTS provider_configuration;
DROP TABLE IF EXISTS provider;
DROP TABLE IF EXISTS workflow;
DROP TABLE IF EXISTS statistics;




CREATE TABLE provider (
    provider_id SERIAL PRIMARY KEY,
    provider_name VARCHAR
);

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

CREATE TABLE service_execution (
    se_id SERIAL  PRIMARY KEY,
    activity_id INTEGER,
    provider_id INTEGER,
    configuration_id INTEGER,
    workflow_execution_id VARCHAR,
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
    CONSTRAINT fk_service_execution_provider FOREIGN KEY (provider_id) REFERENCES provider(provider_id),
    CONSTRAINT fk_service_execution_configuration FOREIGN KEY (configuration_id) REFERENCES provider_configuration(configuration_id),
    CONSTRAINT fk_service_execution_activity FOREIGN KEY (activity_id) REFERENCES workflow_activity(activity_id)
);


CREATE TABLE file (
    file_id SERIAL PRIMARY KEY,
    file_name VARCHAR,
    file_bucket VARCHAR,
    file_path VARCHAR,
    file_size FLOAT,
    file_hash_code VARCHAR,
    CONSTRAINT uk_file_data UNIQUE (file_name, file_bucket, file_path, file_size)
);

CREATE TABLE execution_file (
    ef_id SERIAL  PRIMARY KEY,
    se_id INTEGER,
    file_id INTEGER,
    transfer_duration FLOAT,
    transfer_type VARCHAR CONSTRAINT check_action_type CHECK (transfer_type IN ('consumed', 'produced')),
    CONSTRAINT fk_execution_file_service_execution FOREIGN KEY (se_id) REFERENCES service_execution(se_id),
    CONSTRAINT fk_execution_file_file FOREIGN KEY (file_id) REFERENCES file(file_id)
);

CREATE TABLE statistics (
    statistics_id SERIAL  PRIMARY KEY,
    statistics_name VARCHAR,
    statistics_description VARCHAR
);

CREATE TABLE execution_statistics (
    es_id SERIAL  PRIMARY KEY,
    se_id INTEGER,
    statistics_id INTEGER,
    value_float FLOAT,
    value_integer INTEGER,
    value_string VARCHAR,
    CONSTRAINT fk_execution_statistics_service_execution FOREIGN KEY (se_id) REFERENCES service_execution(se_id),
    CONSTRAINT fk_execution_statistics_statistics FOREIGN KEY (statistics_id) REFERENCES statistics(statistics_id)
);


-- Criação da tabela task
CREATE TABLE task (
    task_id SERIAL PRIMARY KEY,
    workflow_activity_id INTEGER NOT NULL,
    FOREIGN KEY (workflow_activity_id) REFERENCES workflow_activity(activity_id)
);



-- Criação da tabela task_file para associar tasks a múltiplos arquivos de entrada
CREATE TABLE task_file (
    tf_id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES task(task_id),
    FOREIGN KEY (file_id) REFERENCES file(file_id),
    UNIQUE (task_id, file_id)
);



update service_execution se set configuration_id = case 
			when se.activity_id = 1 then 1
			when se.activity_id = 2 then 2
			when se.activity_id = 3 then 3
			when se.activity_id = 4 then 1
		end ;
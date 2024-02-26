DROP TABLE IF EXISTS execution_statistics;
DROP TABLE IF EXISTS execution_file;
DROP TABLE IF EXISTS service_execution;
DROP TABLE IF EXISTS workflow_activity;
DROP TABLE IF EXISTS file;
DROP TABLE IF EXISTS service_provider;
DROP TABLE IF EXISTS workflow;
DROP TABLE IF EXISTS statistics;




CREATE TABLE service_provider (
    provider_id SERIAL  PRIMARY KEY,
    provider_name VARCHAR,
    provider_memory INTEGER,
    provider_timeout INTEGER,
    provider_cpu INTEGER.
    provider_storage_mb INTEGER
);

CREATE TABLE workflow (
    id SERIAL  PRIMARY KEY,
    name VARCHAR,
    description VARCHAR
);

CREATE TABLE workflow_activity (
    id SERIAL  PRIMARY KEY,
    name VARCHAR,
    description VARCHAR,
    workflow_id INTEGER,
    CONSTRAINT fk_workflow_activity_workflow FOREIGN KEY (workflow_id) REFERENCES workflow(id)
);

CREATE TABLE service_execution (
    id SERIAL  PRIMARY KEY,
    activity_id INTEGER,
    provider_id INTEGER,
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
    CONSTRAINT fk_service_execution_service_provider FOREIGN KEY (provider_id) REFERENCES service_provider(provider_id),
    CONSTRAINT fk_service_execution_workflow_activity FOREIGN KEY (activity_id) REFERENCES workflow_activity(id)
);


CREATE TABLE file (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    bucket VARCHAR,
    path VARCHAR,
    size FLOAT,
    CONSTRAINT uk_file_data UNIQUE (name, size, path, bucket)
);

CREATE TABLE execution_file (
    id SERIAL  PRIMARY KEY,
    service_execution_id INTEGER,
    file_id INTEGER,
    transfer_duration FLOAT,
    transfer_type VARCHAR(10) CONSTRAINT check_action_type CHECK (transfer_type IN ('consumed', 'produced')),
    CONSTRAINT fk_execution_file_service_execution FOREIGN KEY (service_execution_id) REFERENCES service_execution(id),
    CONSTRAINT fk_execution_file_file FOREIGN KEY (file_id) REFERENCES file(id)
);

CREATE TABLE statistics (
    id SERIAL  PRIMARY KEY,
    name VARCHAR,
    description VARCHAR
);

CREATE TABLE execution_statistics (
    id SERIAL  PRIMARY KEY,
    service_execution_id INTEGER,
    statistics_id INTEGER,
    value_float FLOAT,
    value_integer INTEGER,
    value_string VARCHAR,
    CONSTRAINT fk_execution_statistics_service_execution FOREIGN KEY (service_execution_id) REFERENCES service_execution(id),
    CONSTRAINT fk_execution_statistics_statistics FOREIGN KEY (statistics_id) REFERENCES statistics(id)
);

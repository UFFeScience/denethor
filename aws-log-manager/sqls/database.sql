DROP TABLE IF EXISTS execution_statistics CASCADE;
DROP TABLE IF EXISTS service_execution CASCADE;
DROP TABLE IF EXISTS workflow_activity CASCADE;
DROP TABLE IF EXISTS file CASCADE;
DROP TABLE IF EXISTS service_provider CASCADE;
DROP TABLE IF EXISTS workflow CASCADE;
DROP TABLE IF EXISTS statistics CASCADE;

CREATE TABLE file (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE,
    size FLOAT,
    path VARCHAR
);

CREATE TABLE statistics (
    id SERIAL  PRIMARY KEY,
    name VARCHAR
);

CREATE TABLE service_provider (
    id SERIAL  PRIMARY KEY,
    name VARCHAR,
    memory INTEGER,
    timeout INTEGER,
    cpu INTEGER
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
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration INTEGER,
    error_message VARCHAR,
    activity_id INTEGER,
    service_id INTEGER,
    consumed_file_id INTEGER,
    produced_file_id INTEGER,
    CONSTRAINT fk_service_execution_service_provider FOREIGN KEY (service_id) REFERENCES service_provider(id),
    CONSTRAINT fk_service_execution_workflow_activity FOREIGN KEY (activity_id) REFERENCES workflow_activity(id),
    CONSTRAINT fk_service_execution_consumed_file_id FOREIGN KEY (consumed_file_id) REFERENCES file(id),
    CONSTRAINT fk_service_execution_produced_file_id FOREIGN KEY (produced_file_id) REFERENCES file(id)
);

CREATE TABLE execution_statistics (
    id SERIAL  PRIMARY KEY,
    value_float FLOAT,
    value_integer INTEGER,
    value_string VARCHAR,
    service_execution_id INTEGER,
    statistics_id INTEGER,
    CONSTRAINT fk_execution_statistics_service_execution FOREIGN KEY (service_execution_id) REFERENCES service_execution(id),
    CONSTRAINT fk_execution_statistics_statistics FOREIGN KEY (statistics_id) REFERENCES statistics(id)
);




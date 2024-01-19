DROP TABLE IF EXISTS execution_statistics CASCADE;
DROP TABLE IF EXISTS service_execution CASCADE;
DROP TABLE IF EXISTS workflow_activity CASCADE;
DROP TABLE IF EXISTS file CASCADE;
DROP TABLE IF EXISTS service_provider CASCADE;
DROP TABLE IF EXISTS workflow CASCADE;
DROP TABLE IF EXISTS statistics CASCADE;




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

CREATE TABLE file (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    size FLOAT,
    path VARCHAR,
    bucket VARCHAR,
    CONSTRAINT uk_file_data UNIQUE (name, size, path, bucket)
);

CREATE TABLE service_execution (
    id SERIAL  PRIMARY KEY,
    request_id VARCHAR,
    log_stream_name VARCHAR,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    duration FLOAT,
    billed_duration FLOAT,
    init_duration FLOAT,
    consumed_file_download_duration FLOAT,
    produced_file_upload_duration FLOAT,
    memory_size INTEGER,
    max_memory_used INTEGER,
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


CREATE TABLE statistics (
    id SERIAL  PRIMARY KEY,
    name VARCHAR
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



INSERT INTO service_provider (name, memory, timeout, cpu) VALUES ('AWS Lambda', 128, null, null);

INSERT INTO workflow (name, description) VALUES
    ('aws_lambda_eval', 
    'Performance Evaluation of Lambda Functions in AWS'
    );

INSERT INTO workflow_activity (name, description, workflow_id) VALUES
    ('tree_constructor', 
    'Construção de árvores filogenéticas a partir das sequências de proteínas fornecidas',
    (select id from workflow where name = 'aws_lambda_eval')
    );
    
INSERT INTO workflow_activity (name, description, workflow_id) VALUES 
    ('find_subtree', 
    'Geração de subárvores a partir das árvores principais e análise de MAF (matriz de frequência de pares de subárvores)',
    (select id from workflow where name = 'aws_lambda_eval')
    );
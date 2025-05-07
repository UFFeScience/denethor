-- DROP VIEW IF EXISTS vw_file_type;
-- DROP VIEW IF EXISTS vw_service_execution_info_recent;
-- DROP VIEW IF EXISTS vw_service_execution_info;
-- DROP VIEW IF EXISTS vw_task;
-- DROP VIEW IF EXISTS vw_service_execution_task;


-- DROP TABLE IF EXISTS public.execution_statistics;
-- DROP TABLE IF EXISTS public."statistics";
-- DROP TABLE IF EXISTS public.execution_file;
-- DROP TABLE IF EXISTS public."file";
-- DROP TABLE IF EXISTS public.task;
-- DROP TABLE IF EXISTS public.service_execution;
-- DROP TABLE IF EXISTS public.workflow_execution;
-- DROP TABLE IF EXISTS public.workflow_activity;
-- DROP TABLE IF EXISTS public.workflow;
-- DROP TABLE IF EXISTS public.provider_configuration;
-- DROP TABLE IF EXISTS public."provider";




CREATE TABLE provider (
    provider_id SERIAL PRIMARY KEY,
    provider_name VARCHAR NOT NULL,
    provider_tag VARCHAR NOT NULL
);

-- Adding indices for provider table
CREATE INDEX idx_provider_provider_tag ON provider (provider_tag);




CREATE TABLE provider_configuration (
    conf_id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL,
    timeout INTEGER NOT NULL,
    cpu INTEGER NOT NULL,
    memory_mb INTEGER NOT NULL,
    storage_mb INTEGER NOT NULL,
    FOREIGN KEY (provider_id) REFERENCES provider(provider_id)
);

-- Adding indices for provider_configuration table
CREATE INDEX idx_provider_configuration_provider_id ON provider_configuration (provider_id);




CREATE TABLE workflow (
    workflow_id SERIAL PRIMARY KEY,
    workflow_name VARCHAR NOT NULL,
    workflow_description VARCHAR
);

-- Adding indices for workflow table
CREATE INDEX idx_workflow_workflow_name ON workflow (workflow_name);




CREATE TABLE workflow_activity (
    activity_id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL,
    activity_name VARCHAR NOT NULL,
    activity_description VARCHAR,
    FOREIGN KEY (workflow_id) REFERENCES workflow(workflow_id)
);

-- Adding indices for workflow_activity table
CREATE INDEX idx_workflow_activity_workflow_id ON workflow_activity (workflow_id);




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

-- Adding indices for workflow_execution table
CREATE INDEX idx_workflow_execution_workflow_id ON workflow_execution (workflow_id);
CREATE INDEX idx_workflow_execution_execution_tag ON workflow_execution (execution_tag);




CREATE TABLE task (
    task_id INTEGER PRIMARY KEY,
    activity_id INTEGER NOT NULL,
    execution_count INTEGER NOT NULL,
    task_type INTEGER NOT NULL,
    input_count INTEGER NOT NULL,
    output_count INTEGER NOT NULL,
    input_list TEXT NOT NULL,
    output_list TEXT NOT NULL,
    FOREIGN KEY (activity_id) REFERENCES workflow_activity(activity_id),
    UNIQUE (activity_id, input_list, output_list)

);

-- Adding indices for task table
CREATE INDEX idx_task_activity_id ON task (activity_id);
CREATE INDEX idx_task_input_list_output_list ON task (input_list, output_list);




CREATE TABLE service_execution (
    se_id SERIAL  PRIMARY KEY,
    --task_id INTEGER,
    we_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    provider_conf_id INTEGER NOT NULL,
    request_id VARCHAR NOT NULL,
    log_stream_name VARCHAR,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
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
    FOREIGN KEY (provider_conf_id) REFERENCES provider_configuration(conf_id)--,
    --FOREIGN KEY (task_id) REFERENCES task(task_id)
);

-- Adding indices for service_execution table
CREATE INDEX idx_service_execution_activity_id ON service_execution (activity_id);
CREATE INDEX idx_service_execution_we_id ON service_execution (we_id);
CREATE INDEX idx_service_execution_provider_conf_id ON service_execution (provider_conf_id);
--CREATE INDEX idx_service_execution_task_id ON service_execution (task_id);
CREATE INDEX idx_service_execution_start_time ON service_execution (start_time);

-- Adding column for storing original values
ALTER TABLE service_execution ADD COLUMN original_values TEXT;


-- Adding column to indicate that the consumed_files_transfer_duration is updated with transfer_duration
ALTER TABLE service_execution ADD COLUMN updated_consumed_duration BOOLEAN DEFAULT FALSE;

-- Adding column to indicate that the duration is updated with consumed_files_transfer_duration
ALTER TABLE service_execution ADD COLUMN updated_duration BOOLEAN DEFAULT FALSE;

-- Adding column to indicate that the billed duration is updated with consumed_files_transfer_duration
ALTER TABLE service_execution ADD COLUMN updated_billed_duration BOOLEAN DEFAULT FALSE;




CREATE TABLE file (
    file_id SERIAL PRIMARY KEY,
    file_name VARCHAR NOT NULL,
    file_bucket VARCHAR,
    file_path VARCHAR,
    file_size FLOAT NOT NULL,
    file_hash_code VARCHAR NOT NULL,
    UNIQUE (file_name, file_bucket, file_path, file_size)
);

-- Adding indices for file table
CREATE INDEX idx_file_file_name ON file (file_name);

-- Adding composite index for file table
CREATE INDEX idx_file_name_bucket_path ON file (file_name, file_bucket, file_path);

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

-- Adding indices for execution_file table
CREATE INDEX idx_execution_file_se_id ON execution_file (se_id);
CREATE INDEX idx_execution_file_file_id ON execution_file (file_id);
CREATE INDEX idx_execution_file_transfer_type ON execution_file (transfer_type);
CREATE INDEX idx_execution_file_transfer_duration ON execution_file (transfer_duration);

-- Composite index for frequent filtering and joining
CREATE INDEX idx_execution_file_se_id_transfer_type ON execution_file (se_id, transfer_type);




CREATE TABLE statistics (
    statistics_id SERIAL  PRIMARY KEY,
    statistics_name VARCHAR NOT NULL,
    statistics_description VARCHAR NOT NULL
);

-- Adding indices for statistics table
CREATE INDEX idx_statistics_statistics_name ON statistics (statistics_name);




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

-- Adding indices for execution_statistics table
CREATE INDEX idx_execution_statistics_se_id ON execution_statistics (se_id);
CREATE INDEX idx_execution_statistics_statistics_id ON execution_statistics (statistics_id);




-- Insert only the new tasks from the vw_task view
-- INSERT INTO task (task_id, activity_id, execution_count, task_type, input_count, output_count, input_list, output_list)
-- SELECT 
--     ta.task_id,
--     ta.activity_id,
--     ta.execution_count,
--     ta.task_type,
--     ta.consumed_files_count as input_count,
--     ta.produced_files_count as output_count,
--     ta.consumed_files_list  as input_list,
--     ta.produced_files_list  as output_list
-- FROM vw_task ta
-- WHERE ta.task_id NOT IN (SELECT task_id FROM task);

-- -- Update task_id in service_execution when it is NULL
-- UPDATE service_execution
-- SET task_id = vw.task_id
-- FROM vw_service_execution_task vw
-- WHERE service_execution.se_id = vw.se_id
--   AND service_execution.task_id IS NULL;




CREATE TABLE vm_configurations (
    vm_id INTEGER PRIMARY KEY,
    vm_type VARCHAR(50) NOT NULL,
    vcpu INTEGER NOT NULL,
    cpu_slowdown DECIMAL(5, 2) NOT NULL,
    cost DECIMAL(18, 10) NOT NULL,
    storage INTEGER NOT NULL,
    bandwidth INTEGER NOT NULL
);

-- Adding indices for vm_configurations table
CREATE INDEX idx_vm_configurations_vm_type ON vm_configurations (vm_type);

INSERT INTO vm_configurations (vm_id, vm_type, vcpu, cpu_slowdown, cost, storage, bandwidth)
VALUES
    (1, 't2.micro',  1, 1,   0.0000051670, 8192, 1250),
    (2, 't2.small',  2, 1,   0.0000103330, 8192, 1250),
    (3, 't2.medium', 2, 0.5, 0.0000186671, 8192, 5000);




CREATE TABLE bucket_ranges (
    bucket_range_id INTEGER PRIMARY KEY,
    size1_gb BIGINT NOT NULL,
    size2_gb BIGINT NOT NULL,
    cost_per_gb DECIMAL(10, 4) NOT NULL
);

-- Adding indices for bucket_ranges table
CREATE INDEX idx_bucket_ranges_size1_size2 ON bucket_ranges (size1_gb, size2_gb);

-- Inserindo os dados na nova tabela
INSERT INTO bucket_ranges (bucket_range_id, size1_gb, size2_gb, cost_per_gb)
VALUES
    (1, 0, 50*1024, 0.0405),
    (2, 50*1024, 450*1024, 0.039),
    (3, 450*1024, 99999999999999, 0.037);




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
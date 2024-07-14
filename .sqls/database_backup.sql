CREATE TABLE bkp2_service_provider AS SELECT * FROM service_provider;
CREATE TABLE bkp2_workflow AS SELECT * FROM workflow;
CREATE TABLE bkp2_workflow_activity AS SELECT * FROM workflow_activity;
CREATE TABLE bkp2_service_execution AS SELECT * FROM service_execution;
CREATE TABLE bkp2_file AS SELECT * FROM file;
CREATE TABLE bkp2_execution_file AS SELECT * FROM execution_file;
CREATE TABLE bkp2_statistics AS SELECT * FROM statistics;
CREATE TABLE bkp2_execution_statistics AS SELECT * FROM execution_statistics;

DECLARE @prefix VARCHAR(100) = 'bkp2';
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql += 'DROP TABLE ' + QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME) + ';'
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE @prefix + '%';

EXEC sp_executesql @sql;
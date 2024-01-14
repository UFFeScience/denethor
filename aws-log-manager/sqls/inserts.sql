INSERT INTO service_provider (name, memory, timeout, cpu) VALUES ('AWS Lambda', 128, null, null);

INSERT INTO statistics (name) VALUES ('upload_duration');
INSERT INTO statistics (name) VALUES ('download_duration');

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
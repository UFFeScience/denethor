import psycopg2

conn = connect()

def connect():
    # Parâmetros de conexão
    host = 'mribeiro-pg-database.ca8aozgznnhf.sa-east-1.rds.amazonaws.com'
    port = 5432
    database = 'postgres'
    user = 'postgres'
    password = 'postgres'

    try:
        # Conectando ao banco de dados
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Função para inserir dados na tabela service_provider
def insert_service_provider(name, memory, timeout, cpu):
    try:
        # Inserindo dados na tabela service_provider
        cur = conn.cursor()
        cur.execute("INSERT INTO service_provider (name, memory, timeout, cpu) VALUES (%s, %s, %s, %s)", (name, memory, timeout, cpu))

        # Exibindo os dados da tabela service_provider
        cur.execute("SELECT * FROM service_provider")
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Função para inserir dados na tabela workflow
def insert_workflow(name, description):
    try:
        # Inserindo dados na tabela workflow
        cur = conn.cursor()
        cur.execute("INSERT INTO workflow (name, description) VALUES (%s, %s)", (name, description))

        # Exibindo os dados da tabela workflow
        cur.execute("SELECT * FROM workflow")
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Função para inserir dados na tabela service_execution
def insert_service_execution(startTime, endTime, errorMessage, activityID, serviceID, consumedFileID, producedFileID):
    try:
        # Inserindo dados na tabela service_execution
        cur = conn.cursor()
        cur.execute("INSERT INTO service_execution (start_time, end_time, error_message, activity_id, service_id, consumed_file_id, produced_file_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (startTime, endTime, errorMessage, activityID, serviceID, consumedFileID, producedFileID))

        # Exibindo os dados da tabela service_execution
        cur.execute("SELECT * FROM service_execution")
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Função para inserir dados na tabela file
def insert_file(name, size, path):
    try:
        # Inserindo dados na tabela file
        cur = conn.cursor()
        cur.execute("INSERT INTO file (name, size, path) VALUES (%s, %s, %s)", (name, size, path))

        # Exibindo os dados da tabela file
        cur.execute("SELECT * FROM file")
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")


# Função para inserir dados na tabela workflow_activity
def insert_workflow_activity(name, workflowID):
    try:
        # Inserindo dados na tabela workflow_activity
        cur = conn.cursor()
        cur.execute("INSERT INTO workflow_activity (name, workflow_id) VALUES (%s, %s)", (name, workflowID))

        # Exibindo os dados da tabela workflow_activity
        cur.execute("SELECT * FROM workflow_activity")
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")


# Função para inserir dados na tabela execution_statistics
def insert_execution_statistics(valueFloat, valueInteger, valueString, serviceExecutionID, statisticsID):
    try:
        # Inserindo dados na tabela execution_statistics
        cur = conn.cursor()
        cur.execute("INSERT INTO execution_statistics (value_float, value_integer, value_string, service_execution_id, statistics_id) VALUES (%s, %s, %s, %s, %s)", (valueFloat, valueInteger, valueString, service_executionID, statisticsID))

        # Exibindo os dados da tabela execution_statistics
        cur.execute("SELECT * FROM execution_statistics")
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Função para inserir dados na tabela statistics
def insert_statistics(name):
    try:
        # Inserindo dados na tabela statistics
        cur = conn.cursor()
        cur.execute("INSERT INTO statistics (name) VALUES (%s)", (name,))

        # Exibindo os dados da tabela statistics
        cur.execute("SELECT * FROM statistics")
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

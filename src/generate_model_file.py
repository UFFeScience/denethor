import os, re
from denethor.database.conn import Connection
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


# WEID = 'weid_1724184708846' #002
# WEID = 'weid_1724428668735' #005
# WEID = 'weid_1724433692051' #010
WEID = 'weid_1722560049311' #050

SQL_FILES_PATH = 'resources/sql/model_generator'  # Diretório onde os arquivos SQL estão localizados

WRITE_COMMENTS_TO_FILE = True

# Remover Comentários de um Script SQL
def remove_comments(sql):
    lines = sql.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith('--')]
    return '\n'.join(filtered_lines)

def separate_comments_and_code(sql):
    lines = sql.split('\n')
    comments = []
    code = []
    
    for line in lines:
        if line.strip().startswith('--'):
            comments.append(line.strip())
        else:
            code.append(line)
    
    comments_str = '\n'.join(comments)
    code_str = '\n'.join(code)
    
    return comments_str, code_str

# Buscar todas as ocorrências de weid_\d+ ou '[weid]' no script SQL
def find_weid_occurrences(sql):
    pattern = r'weid_\d+|\[weid\]'
    return list(set(re.findall(pattern, sql)))

def replace_weid(sql):
    weid_occurrences = find_weid_occurrences(sql)
    for occurrence in weid_occurrences:
        sql = sql.replace(occurrence, WEID)
    return sql

def execute_sql_with_weid(sql_file, output_file, session):
    print(f"Executing {sql_file} with weid {WEID}")

    sql_file_path = os.path.join(SQL_FILES_PATH, sql_file)

    with open(sql_file_path, 'r') as file:
        sql = file.read()
    
    # remove comments
    # sql = remove_comments(sql)

    # separate comments and code
    comments, sql = separate_comments_and_code(sql)

    # replace weid
    sql = replace_weid(sql)
    
    try:
        result = session.execute(text(sql))
        results = result.fetchall()
        
        with open(output_file, 'a') as out_file:
            # out_file.write(f"-----------{sql_file}\n")
            if WRITE_COMMENTS_TO_FILE:
                out_file.write(comments + '\n')
            for row in results:
                out_file.write('\t'.join(map(str, row)) + '\n')
            out_file.write('\n')
    
    except SQLAlchemyError as e:
        print(f"Error executing {sql_file}: {e}")
    
    finally:
        session.close()

def execute_sql_instance_count(session):
    
    SQL_COUNT = f"SELECT to_char(count(distinct se.task_id), 'fm000') AS inst_count \
    FROM service_execution se \
    WHERE se.activity_id = 1 and \
          se.workflow_execution_id in ('{WEID}')"

    try:
        result = session.execute(text(SQL_COUNT))
        return result.scalar()
    except SQLAlchemyError as e:
        print(f"Error executing instance count SQL: {e}")
        return None
    finally:
        session.close()

def main():
    
    print(f"Generating model file for WEID: {WEID}")

    # Conecte-se ao banco de dados PostgreSQL
    connection = Connection()
    session = connection.get_session()
    
    # execute sql instance count
    count = execute_sql_instance_count(session)
    OUTPUT_FILE_NAME = f'model_instance_{count}_{WEID}.txt'
    
    if os.path.exists(OUTPUT_FILE_NAME):
        os.remove(OUTPUT_FILE_NAME)
    
    # Listar todos os arquivos .sql no diretório especificado e ordenar por nome
    sql_files = sorted([f for f in os.listdir(SQL_FILES_PATH) if f.endswith('.sql')])

    for sql_file in sql_files:
        execute_sql_with_weid(sql_file, OUTPUT_FILE_NAME, session)

if __name__ == "__main__":
    main()
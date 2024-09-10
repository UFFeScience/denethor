import os, re
from denethor.database.conn import Connection
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


WEID = 'weid_1724428668735'  # Substitua pelo WEID desejado

OUTPUT_FILE_NAME = f'model_{WEID}.txt'  # Nome do arquivo de saída contendo o modelo gerado

SQL_FILES_PATH = 'resources/sql/model_generator'  # Diretório onde os arquivos SQL estão localizados

# Remover Comentários de um Script SQL
def remove_comments(sql):
    lines = sql.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith('--')]
    return '\n'.join(filtered_lines)

# Buscar todas as ocorrências de weid_\d+ ou '[weid]' no script SQL
def find_weid_occurrences(sql):
    pattern = r'weid_\d+|\[weid\]'
    return list(set(re.findall(pattern, sql)))

def replace_weid(sql):
    weid_occurrences = find_weid_occurrences(sql)
    for occurrence in weid_occurrences:
        sql = sql.replace(occurrence, WEID)
    return sql

def execute_sql_with_weid(sql_file):
    print(f"Executing {sql_file} with weid {WEID}")

    sql_file_path = os.path.join(SQL_FILES_PATH, sql_file)

    with open(sql_file_path, 'r') as file:
        sql = file.read()
    
    # remove comments
    sql = remove_comments(sql)

    # replace weid
    sql = replace_weid(sql)
    
    
    # Conecte-se ao banco de dados PostgreSQL
    connection = Connection()
    session = connection.get_session()
    
    try:
        result = session.execute(text(sql))
        results = result.fetchall()
        
        with open(OUTPUT_FILE_NAME, 'a') as out_file:
            out_file.write(f"-----------{sql_file}\n")
            for row in results:
                out_file.write('\t'.join(map(str, row)) + '\n')
    
    except SQLAlchemyError as e:
        print(f"Error executing {sql_file}: {e}")
    
    finally:
        session.close()

def main():
    print(f"Generating model file for WEID: {WEID}")
    
    if os.path.exists(OUTPUT_FILE_NAME):
        os.remove(OUTPUT_FILE_NAME)
    
    # Listar todos os arquivos .sql no diretório especificado e ordenar por nome
    sql_files = sorted([f for f in os.listdir(SQL_FILES_PATH) if f.endswith('.sql')])

    for sql_file in sql_files:
        execute_sql_with_weid(sql_file)

if __name__ == "__main__":
    main()
import os
from denethor.database.conn import Connection
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def remove_comments(sql):
    lines = sql.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith('--')]
    return '\n'.join(filtered_lines)

def execute_sql_with_weid(sql_file, sql_path, weid, output_file):
    print(f"Executing {sql_file} with weid {weid}")

    sql_file_path = os.path.join(sql_path, sql_file)

    with open(sql_file_path, 'r') as file:
        sql = file.read()
    
    sql = remove_comments(sql)
    sql = sql.replace('[weid]', weid)
    
    # Conecte-se ao banco de dados PostgreSQL
    connection = Connection()
    session = connection.get_session()
    
    try:
        result = session.execute(text(sql))
        results = result.fetchall()
        
        with open(output_file, 'a') as out_file:
            out_file.write(f"-----------{sql_file}\n")
            for row in results:
                out_file.write('\t'.join(map(str, row)) + '\n')
    
    except SQLAlchemyError as e:
        print(f"Error executing {sql_file}: {e}")
    
    finally:
        session.close()

def main():
    weid = 'weid_1234567890'  # Substitua pelo valor desejado
    output_file = f"model_{weid}.txt"
    sql_path = 'resources/sql/model_generator'  # Diretório onde os arquivos SQL estão localizados
    
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Listar todos os arquivos .sql no diretório especificado e ordenar por nome
    sql_files = sorted([f for f in os.listdir(sql_path) if f.endswith('.sql')])

    for sql_file in sql_files:
        execute_sql_with_weid(sql_file, sql_path, weid, output_file)

if __name__ == "__main__":
    main()
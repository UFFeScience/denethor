import os, re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from denethor.core.database.conn import Connection
from instance_generator import utils as igu
from datetime import datetime

#config basica: 128 + 256 + 512 + 128
# WEID = 'weid_1724184708846' // weid_1730480017077  #002
# WEID = 'weid_1724428668735' // weid_1730479857730  #005
# WEID = 'weid_1724433692051' #010
# WEID = 'weid_1722560049311' #050

# config: 256 + 512 + 1024 + 128
# WEID = 'weid_1730474091468' #002
# WEID = 'weid_1729872467000' #005

# 002 / config n1 + n2
# WEID = ['weid_1730480017077', 'weid_1730474091468']

# 005 / config n1 + n2
# WEID = ['weid_1730479857730', 'weid_1729872467000']

# 2 files with:

#       128mb
# WEID = ['weid_1735311414938']

#       128mb               / 256mb               / 512                  / 1024               / 2048 execution
#WEID = ['weid_1735311414938', 'weid_1735318446694', 'weid_1735319031426', 'weid_1735319100179', 'weid_1735319150437']


WETAG = ['wetag_1741230695726']

SQL_FILES_PATH = 'resources/sql/instance_generator/'  # Diretório onde os arquivos SQL estão localizados

INSTANCE_FILE_PATH = 'resources/data/instance_files/'  # Diretório onde os arquivos de instância serão salvos

WRITE_COMMENTS_TO_FILE = True



def main():
    
    print(f"Generating model file for execution_tag: {WETAG}")

    # Conecte-se ao banco de dados PostgreSQL
    connection = Connection()
    session = connection.get_session()

    execution_tag = ','.join(f"'{tag}'" for tag in WETAG)  # Adiciona aspas simples ao redor de cada elemento

    # execute sql instance count
    count = igu.execute_sql_instance_count(execution_tag, session)
    out_file_name = f'model_instance_{count}_{execution_tag}.txt'.replace(',', '__').replace("'", '')
    
    out_file = os.path.join(INSTANCE_FILE_PATH, out_file_name)

    if os.path.exists(out_file):
        os.remove(out_file)
    
    output_sqls_file = out_file.replace('.txt', '_executed.sql')
    if os.path.exists(output_sqls_file):
        os.remove(output_sqls_file)

    # Listar todos os arquivos .sql no diretório especificado e ordenar por nome
    sql_files = sorted([f for f in os.listdir(SQL_FILES_PATH) if f.endswith('.sql')])

    for sql_file_name in sql_files:
        
        print(f"Executing {sql_file_name} with execution_tag: {execution_tag}")
        sql_file = os.path.join(SQL_FILES_PATH, sql_file_name)

        execute_sql_and_save_results(execution_tag, sql_file, out_file, output_sqls_file, WRITE_COMMENTS_TO_FILE, session)



# Execute SQL script and save results to a file
def execute_sql_and_save_results(execution_tag, input_sql_file, output_results_file, output_sqls_file, write_sql_comments, db):

    with open(input_sql_file, 'r') as file:
        sql_to_execute = file.read()
    
    # separate comments and code
    comments, sql_to_execute = igu.separate_comments_and_code(sql_to_execute)

    # replace wetag
    sql_to_execute = igu.replace_wetag(execution_tag, sql_to_execute)
    
    try:
        result = db.execute(text(sql_to_execute))
        results = result.fetchall()
        
        with open(output_results_file, 'a') as file:
            # out_file.write(f"-----------{sql_file}\n")
            if write_sql_comments:
                file.write(comments + '\n')
            for row in results:
                file.write('\t'.join(map(str, row)) + '\n')
            file.write('\n')

        # write the executed sql to a file
        with open(output_sqls_file, 'a') as file:
            file.write(f"-----------{input_sql_file}\n")
            file.write(f"-----------{execution_tag}\n")
            file.write(f"-----------Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            file.write(comments + '\n')
            file.write(sql_to_execute + '\n\n')

    
    except SQLAlchemyError as e:
        print(f"Error executing {input_sql_file}: {e}")
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
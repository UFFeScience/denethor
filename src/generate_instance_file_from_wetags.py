import os, re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from denethor.core.database.conn import Connection
from datetime import datetime

SQL_FILES_PATH = 'scripts/sql/instance_generator/'  # Diretório onde os arquivos SQL estão localizados
INSTANCE_FILE_PATH = 'resources/data/instance_files/'  # Diretório onde os arquivos de instância serão salvos
WRITE_COMMENTS_TO_FILE = True

# Connect to the PostgreSQL database
session = Connection().get_session()



# execução em função lambda com 50 entradas e todas as configurações
# execução em vm: xxxx
WETAG_FX = ['wetag_1744757716148', 'wetag_1744767700184', 'wetag_1744771889401', 'xxx', 'xxx']
# WETAG_VM = ['xxxx']



def main():
    
    print(f"Generating model file for execution_tag: {WETAG_FX}")

    execution_tag_fx = ','.join(f"'{tag}'" for tag in WETAG_FX)  # Adiciona aspas simples ao redor de cada elemento

    # execute sql instance count
    count = execute_sql_input_count(execution_tag_fx)
    out_file_name = f'model_instance_{count}_{execution_tag_fx}.txt'.replace(',', '__').replace("'", '')
    
    out_file_data = os.path.join(INSTANCE_FILE_PATH, out_file_name)

    if os.path.exists(out_file_data):
        os.remove(out_file_data)
    
    out_file_sqls = out_file_data.replace('.txt', '_executed.sql')
    if os.path.exists(out_file_sqls):
        os.remove(out_file_sqls)

    # List all .sql files in the specified directory and sort them by name
    sql_files = sorted([f for f in os.listdir(SQL_FILES_PATH) if f.endswith('.sql')])

    for sql_file_name in sql_files:
        
        print(f"Executing {sql_file_name} with execution_tag: {execution_tag_fx}")
        sql_file = os.path.join(SQL_FILES_PATH, sql_file_name)

        execute_sql_and_save_results(execution_tag_fx, sql_file, out_file_data, out_file_sqls, WRITE_COMMENTS_TO_FILE)

    print(f"Model file generated: {out_file_data}")


# Execute SQL script and save results to a file
def execute_sql_and_save_results(execution_tag, input_sql_file, output_results_file, output_sqls_file, write_sql_comments):

    with open(input_sql_file, 'r') as file:
        sql_to_execute = file.read()
    
    # separate comments and code
    comments, sql_to_execute = separate_comments_and_code(sql_to_execute)

    # replace wetag
    sql_to_execute = replace_wetag(execution_tag, sql_to_execute)
    
    try:
        result = session.execute(text(sql_to_execute))
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
        session.close()


# Remove comments from SQL script
def remove_comments(sql):
    lines = sql.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith('--')]
    return '\n'.join(filtered_lines)


# This function separates comments (starting with '--#') from the SQL code
# and returns them as two separate strings.
def separate_comments_and_code(sql: str):
    lines = sql.split('\n')
    comments = []
    code = []
    
    for line in lines:
        if line.strip().startswith('--#'):
            comments.append(line.strip().replace('--',''))
        else:
            code.append(line)
    
    comments_str = '\n'.join(comments)
    code_str = '\n'.join(code)
    
    return comments_str, code_str


# Find all occurrences of wetag_\d+ or [wetag] in the SQL script
def replace_wetag(execution_tag, sql):
    pattern = r'wetag_\d+|\[wetag\]'
    wetag_occurrences = list(set(re.findall(pattern, sql)))
    
    for occurrence in wetag_occurrences:
        sql = sql.replace(occurrence, execution_tag)
        sql = sql.replace("''", "'")
    return sql


# Execute SQL to get the input count for the given execution tag
def execute_sql_input_count(execution_tag: list):
    SQL_INPUT_COUNT = f"\
        SELECT max(input_count) \
        FROM workflow_execution we \
        WHERE we.execution_tag in ({execution_tag})"
    
    print(f"Executing SQL: {SQL_INPUT_COUNT}")

    try:
        result = session.execute(text(SQL_INPUT_COUNT))
        return result.scalar()
    except SQLAlchemyError as e:
        print(f"Error executing instance count SQL: {e}")
        return None
    finally:
        session.close()



if __name__ == "__main__":
    main()
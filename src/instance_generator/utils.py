import os, re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Remover Comentários de um Script SQL
def remove_comments(sql):
    lines = sql.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith('--')]
    return '\n'.join(filtered_lines)


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


# Buscar todas as ocorrências de weid_\d+ ou '[weid]' no script SQL
def find_weid_occurrences(sql):
    pattern = r'weid_\d+|\[weid\]'
    return list(set(re.findall(pattern, sql)))


def replace_weid(weid_str, sql):
    weid_occurrences = find_weid_occurrences(sql)
    
    for occurrence in weid_occurrences:
        sql = sql.replace(occurrence, weid_str)
        sql = sql.replace("''", "'")
    return sql


def execute_sql_instance_count(weid_str: list, session):
    SQL_COUNT = f"\
        SELECT to_char(count(distinct se.task_id), 'fm000') AS inst_count \
        FROM service_execution se \
        WHERE se.activity_id = 1 and \
              se.workflow_execution_id in ({weid_str})"
    
    print(f"Executing SQL: {SQL_COUNT}")

    try:
        result = session.execute(text(SQL_COUNT))
        return result.scalar()
    except SQLAlchemyError as e:
        print(f"Error executing instance count SQL: {e}")
        return None
    finally:
        session.close()
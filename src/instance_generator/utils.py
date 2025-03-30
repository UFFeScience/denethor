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


# Buscar todas as ocorrências de wetag_\d+ ou '[wetag]' no script SQL
def find_wetag_occurrences(sql):
    pattern = r'wetag_\d+|\[wetag\]'
    return list(set(re.findall(pattern, sql)))


def replace_wetag(execution_tag, sql):
    wetag_occurrences = find_wetag_occurrences(sql)
    
    for occurrence in wetag_occurrences:
        sql = sql.replace(occurrence, execution_tag)
        sql = sql.replace("''", "'")
    return sql


def execute_sql_instance_count(execution_tag: list, session):
    SQL_COUNT = f"\
        SELECT to_char(count(distinct st.task_id), 'fm000') AS inst_count \
        FROM service_execution se \
        JOIN workflow_execution we on we.we_id = se.we_id\
        JOIN vw_service_execution_task st on st.se_id = se.se_id \
        WHERE se.activity_id = 1 and \
              we.execution_tag in ({execution_tag})"
    
    print(f"Executing SQL: {SQL_COUNT}")

    try:
        result = session.execute(text(SQL_COUNT))
        return result.scalar()
    except SQLAlchemyError as e:
        print(f"Error executing instance count SQL: {e}")
        return None
    finally:
        session.close()
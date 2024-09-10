import pandas as pd
from sqlalchemy.orm import sessionmaker
from denethor.database.conn import Connection
from denethor.database.model import Task, TaskFile

# Configuração do SQLAlchemy
session = Connection().get_session()


# Ler o arquivo CSV
df = pd.read_csv('/home/marcello/Documents/denethor/src/denethor/task.csv', sep='\t', header=0, names=['line', 'workflow_activity_id', 'other_column', 'file_ids'])

# Inserir dados nas tabelas task e task_file
for index, row in df.iterrows():
    # Inserir na tabela task
    task = Task(workflow_activity_id=row['workflow_activity_id'])
    session.add(task)
    session.commit()  # Commit para garantir que task_id seja gerado
    
    # Inserir na tabela task_file
    if pd.notna(row['file_ids']):
        file_ids = row['file_ids'].strip('"').split(', ')
        for file_id in file_ids:
            task_file = TaskFile(task_id=task.task_id, file_id=int(file_id))
            session.add(task_file)

# Commit final para salvar todas as inserções
session.commit()

# Fechar a sessão
session.close()
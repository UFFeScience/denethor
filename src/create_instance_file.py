import os
from denethor.database.conn import Connection
from instance_generator import utils as igu

#config basica: 128 + 256 + 512 + 128
# WEID = 'weid_1724184708846' // weid_1730480017077  #002
# WEID = 'weid_1724428668735' // weid_1730479857730  #005
# WEID = 'weid_1724433692051' #010
# WEID = 'weid_1722560049311' #050

# config: 256 + 512 + 1024 + 128
# WEID = 'weid_1730474091468' #002
# WEID = 'weid_1729872467000' #005

# 002 / config n1 + n2
WEID = ['weid_1730480017077', 'weid_1730474091468']

# 005 / config n1 + n2
# WEID = ['weid_1730479857730', 'weid_1729872467000']


SQL_FILES_PATH = 'src/instance_generator/sql'  # Diretório onde os arquivos SQL estão localizados

INSTANCE_FILE_PATH = 'resources/data/instance_files'  # Diretório onde os arquivos de instância serão salvos

WRITE_COMMENTS_TO_FILE = True



def main():
    
    print(f"Generating model file for WEID: {WEID}")

    # Conecte-se ao banco de dados PostgreSQL
    connection = Connection()
    session = connection.get_session()

    weid_str = ','.join(f"'{w}'" for w in WEID)  # Adiciona aspas simples ao redor de cada elemento

    # execute sql instance count
    count = igu.execute_sql_instance_count(weid_str, session)
    out_file_name = f'model_instance_{count}_{weid_str}.txt'.replace(',', '__').replace("'", '')
    
    out_file = os.path.join(INSTANCE_FILE_PATH, out_file_name)

    if os.path.exists(out_file):
        os.remove(out_file)
    
    # Listar todos os arquivos .sql no diretório especificado e ordenar por nome
    sql_files = sorted([f for f in os.listdir(SQL_FILES_PATH) if f.endswith('.sql')])

    for sql_file_name in sql_files:
        
        print(f"Executing {sql_file_name} with weid {weid_str}")
        sql_file = os.path.join(SQL_FILES_PATH, sql_file_name)

        igu.execute_sql_with_weid(weid_str, sql_file, out_file, WRITE_COMMENTS_TO_FILE, session)

if __name__ == "__main__":
    main()
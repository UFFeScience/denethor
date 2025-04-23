import os, re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from denethor.core.database.conn import Connection
from datetime import datetime

SQL_FILES_PATH = "scripts/sql/instance_generator/"  # Diretório onde os arquivos SQL estão localizados
INSTANCE_FILE_PATH = "resources/data/instance_files/"  # Diretório onde os arquivos de instância serão salvos
WRITE_COMMENTS_TO_FILE = True


#run2
INPUT_WEIDS_FX = [135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189]
INPUT_WEIDS_VM = [190,191,192,193,194,195,196,197,198,199,200]


# Connect to the PostgreSQL database
session = Connection().get_session()

def main():

    # Fetch dynamic WEID_PROVIDER_DICT
    weid_provider_dict = fetch_weid_provider_dict(INPUT_WEIDS_FX, INPUT_WEIDS_VM)

    if not weid_provider_dict:
        raise ValueError("Error: Failed to fetch WEID_PROVIDER_DICT dynamically.")

    for input_count, entry in weid_provider_dict.items():
        weids_fx = entry.get("aws_lambda", [])
        weids_vm = entry.get("aws_ec2", [])

        print(f"Generating model file for weid_fx: {weids_fx} and weid_vm: {weids_vm}")

        # execute sql instance count
        count = execute_sql_input_count(weids_fx, weids_vm)

        if count is None or count == 0:
            raise ValueError(
                f"Error: No input count found for weid_fx: {weids_fx} and weid_vm: {weids_vm}"
            )
        if count != int(input_count):
            raise ValueError(
                f"Error: Input count {count} does not match expected count {input_count} for weid_fx: {weids_fx} and weid_vm: {weids_vm}"
            )

        out_file_name = f"model_instance[{count:03d}]_weids_fx[{'-'.join(map(str, weids_fx))}]__weids_vm[{'-'.join(map(str, weids_vm))}].txt"

        out_file_data = os.path.join(INSTANCE_FILE_PATH, out_file_name)

        if os.path.exists(out_file_data):
            os.remove(out_file_data)

        out_file_sqls = out_file_data.replace("model", "sql").replace(".txt", ".sql")
        if os.path.exists(out_file_sqls):
            os.remove(out_file_sqls)

        # List all .sql files in the specified directory and sort them by name
        sql_files = sorted(
            [f for f in os.listdir(SQL_FILES_PATH) if f.endswith(".sql")]
        )

        for sql_file_name in sql_files:

            print(
                f"Executing {sql_file_name} with weid_fx: {weids_fx} and weid_vm: {weids_vm}"
            )
            sql_file = os.path.join(SQL_FILES_PATH, sql_file_name)

            execute_sql_and_save_results(
                weids_fx,
                weids_vm,
                sql_file,
                out_file_data,
                out_file_sqls,
                WRITE_COMMENTS_TO_FILE,
            )

        print(f"Model file generated: {out_file_data}")


# Execute SQL script and save results to a file
def execute_sql_and_save_results(
    weids_fx: list,
    weids_vm: list,
    input_sql_file: str,
    output_results_file: str,
    output_sqls_file: str,
    write_sql_comments: bool,
):

    with open(input_sql_file, "r") as file:
        sql_to_execute = file.read()

    # separate comments and code
    comments, sql_to_execute = separate_comments_and_code(sql_to_execute)

    # replace wetag
    sql_to_execute = (
        sql_to_execute.replace("[we_column]", "we_id")
        .replace("[we_values]", ",".join(map(str, weids_fx)))
        .replace("[we_values_vm]", ",".join(map(str, weids_vm)))
        .replace("[we_values_fx]", ",".join(map(str, weids_fx)))
    )

    try:
        result = session.execute(text(sql_to_execute))
        results = result.fetchall()

        with open(output_results_file, "a") as file:
            # out_file.write(f"-----------{sql_file}\n")
            if write_sql_comments:
                file.write(comments + "\n")
            for row in results:
                file.write("\t".join(map(str, row)) + "\n")
            file.write("\n")

        # write the executed sql to a file
        with open(output_sqls_file, "a") as file:
            file.write(f"--->{input_sql_file}\n")
            file.write(f"--->weids_fx:{weids_fx}\n")
            file.write(f"--->weids_vm:{weids_vm}\n")
            file.write(
                f"--->Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            file.write(comments + "\n")
            file.write(sql_to_execute + "\n\n\n\n")

    except SQLAlchemyError as e:
        print(f"Error executing {input_sql_file}: {e}")

    finally:
        session.close()


# Remove comments from SQL script
def remove_comments(sql):
    lines = sql.split("\n")
    filtered_lines = [line for line in lines if not line.strip().startswith("--")]
    return "\n".join(filtered_lines)


# This function separates comments (starting with '--#') from the SQL code
# and returns them as two separate strings.
def separate_comments_and_code(sql: str):
    lines = sql.split("\n")
    comments = []
    code = []

    for line in lines:
        if line.strip().startswith("--#"):
            comments.append(line.strip().replace("--", ""))
        else:
            code.append(line)

    comments_str = "\n".join(comments)
    code_str = "\n".join(code)

    return comments_str, code_str


# Execute SQL to get the input count for the given execution tag
def execute_sql_input_count(weids_fx: list, weids_vm: list):
    SQL_INPUT_COUNT = f"\
        SELECT max(input_count) \
        FROM workflow_execution we \
        WHERE we.we_id in ({','.join(map(str, weids_fx))}) OR \
              we.we_id in ({','.join(map(str, weids_vm))})"

    print(f"Executing SQL: {SQL_INPUT_COUNT}")

    try:
        result = session.execute(text(SQL_INPUT_COUNT))
        return result.scalar()
    except SQLAlchemyError as e:
        print(f"Error executing instance count SQL: {e}")
        return None
    finally:
        session.close()


def fetch_weid_provider_dict(weids_fx: list, weids_vm: list):
    """
    Executes the SQL query to fetch input_count and provider data dynamically.
    Accepts weids_fx and weids_vm as parameters to filter the query.
    """
    SQL_DYNAMIC_QUERY = """
    WITH provider_weids_data AS (
        SELECT DISTINCT 
            provider_id, 
            provider_tag, 
            workflow_input_count AS input_count,
            ARRAY_AGG(DISTINCT we_id ORDER BY we_id) AS we_ids
        FROM vw_service_execution_detail
        WHERE we_id = ANY(:weids_fx) OR
              we_id = ANY(:weids_vm)
        GROUP BY provider_id, provider_tag, input_count
    )
    SELECT
        input_count,
        jsonb_object_agg(provider_tag, we_ids) AS provider_data
    FROM provider_weids_data
    GROUP BY input_count
    ORDER BY input_count;
    """

    try:
        result = session.execute(
            text(SQL_DYNAMIC_QUERY),
            {"weids_fx": weids_fx, "weids_vm": weids_vm}
        )
        rows = result.fetchall()
        weid_provider_dict = {
            row.input_count: row.provider_data for row in rows
        }
        return weid_provider_dict
    except SQLAlchemyError as e:
        print(f"Error executing dynamic query: {e}")
        return {}
    finally:
        session.close()


if __name__ == "__main__":
    main()

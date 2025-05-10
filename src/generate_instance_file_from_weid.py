import os, re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from denethor.core.database.conn import Connection
from datetime import datetime

SQL_FILES_PATH = "scripts/sql/instance_generator/"  # Diretório onde os arquivos SQL estão localizados
INSTANCE_FILE_PATH = "resources/data/instance_files/"  # Diretório onde os arquivos de instância serão salvos
WRITE_COMMENTS_TO_FILE = True


# run1
# INPUT_WEIDS_FX = [68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123]
# INPUT_WEIDS_VM = [124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134]

# run2
# INPUT_WEIDS_FX = [135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189]
# INPUT_WEIDS_VM = [190,191,192,193,194,195,196,197,198,199,200]

# run3
INPUT_WEIDS_FX = [201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256]
INPUT_WEIDS_VM = [257,258,259,260,261,262,263,264,265,266,267]

# Connect to the PostgreSQL database
session = Connection().get_session()


def main():

    # Fetch dynamic WEID_PROVIDER_DICT
    weid_provider_dict = retrieve_weids_by_provider_in_json(
        INPUT_WEIDS_FX, INPUT_WEIDS_VM
    )

    if not weid_provider_dict:
        raise ValueError("Error: Failed to fetch WEID_PROVIDER_DICT dynamically.")

    for provided_input_count, entry in weid_provider_dict.items():
        weids_fx = entry.get("aws_lambda", [])
        weids_vm = entry.get("aws_ec2", [])

        print(f"Generating model file for weid_fx: {weids_fx} and weid_vm: {weids_vm}")

        # execute sql instance count
        input_count = retrieve_input_count(weids_fx, weids_vm)

        if input_count != int(provided_input_count):
            raise ValueError(
                f"Error: Input count {input_count} does not match expected count {provided_input_count} for weid_fx: {weids_fx} and weid_vm: {weids_vm}"
            )

        # List all .sql files in the specified directory and sort them by name
        sql_files = sorted(
            [f for f in os.listdir(SQL_FILES_PATH) if f.endswith(".sql")]
        )

        # generate model file name
        out_file_name = generate_file_name(
            input_count, weids_fx, weids_vm, SQL_FILES_PATH, sql_files
        )

        out_file_data = os.path.join(INSTANCE_FILE_PATH, out_file_name)
        if os.path.exists(out_file_data):
            os.remove(out_file_data)

        out_file_sqls = os.path.join(
            INSTANCE_FILE_PATH, "sql_" + out_file_name.replace(".txt", ".sql")
        )
        if os.path.exists(out_file_sqls):
            os.remove(out_file_sqls)

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


def generate_file_name(
    input_count: int,
    weids_fx: list[int],
    weids_vm: list[int],
    file_path: str,
    sql_files: list[str],
):
    results = None

    for sql_file_name in sql_files:
        if "totals" in sql_file_name:
            sql_file = os.path.join(file_path, sql_file_name)
            results = execute_sql(sql_file, weids_fx, weids_vm)
            break

    for row in results:
        print(f"Extracting data from row: {row}")
        task_count = row[0]  # <#tasks>
        config_count = row[1]  # <#config>
        data_count = row[2]  # <#data>
        vm_count = row[3]  # <#vms>
        bucket_count = row[4]  # <#buckets>
        bucket_ranges = row[5]  # <#bucket_ranges>
        max_running_time = row[6]  # <max_running_time>
        max_financial_cost = row[7]  # <max_financial_cost>

    # 002_T7_C5_D14_VM3
    out_file_name = f"I{input_count:03d}_T{task_count}_C{config_count}_D{data_count}_VM{vm_count}__fx_weids[{'-'.join(map(str, weids_fx))}]__vm_weids[{'-'.join(map(str, weids_vm))}].txt"
    return out_file_name

def execute_sql(
    sql_file: str,
    weids_fx: list,
    weids_vm: list,
):
    with open(sql_file, "r") as file:
        sql = file.read()

    # replace weids
    sql = (
        sql.replace("[we_column]", "we_id")
        .replace("[we_values]", ",".join(map(str, weids_fx)))
        .replace("[we_values_vm]", ",".join(map(str, weids_vm)))
        .replace("[we_values_fx]", ",".join(map(str, weids_fx)))
    )

    try:
        result = session.execute(text(sql))
        results = result.fetchall()
        return results    
    except SQLAlchemyError as e:
        print(f"Error executing {sql_file}: {e}")
    finally:
        session.close()


# Execute SQL to get the input count for the given execution tag
def retrieve_input_count(weids_fx: list, weids_vm: list):
    SQL_INPUT_COUNT = f"\
        SELECT max(input_count) \
        FROM workflow_execution we \
        WHERE we.we_id in ({','.join(map(str, weids_fx))}) OR \
              we.we_id in ({','.join(map(str, weids_vm))})"

    print(f"Executing SQL: {SQL_INPUT_COUNT}")

    input_count = None
    try:
        result = session.execute(text(SQL_INPUT_COUNT))
        input_count = result.scalar()
    except SQLAlchemyError as e:
        print(f"Error executing instance count SQL: {e}")
    finally:
        session.close()

    if input_count is None or input_count == 0:
        raise ValueError(
            f"Error: No input count found for weid_fx: {weids_fx} and weid_vm: {weids_vm}"
        )
    return input_count


def retrieve_weids_by_provider_in_json(weids_fx: list, weids_vm: list):
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
            text(SQL_DYNAMIC_QUERY), {"weids_fx": weids_fx, "weids_vm": weids_vm}
        )
        rows = result.fetchall()
        weid_provider_dict = {row.input_count: row.provider_data for row in rows}
        return weid_provider_dict
    except SQLAlchemyError as e:
        print(f"Error executing dynamic query: {e}")
        return {}
    finally:
        session.close()


if __name__ == "__main__":
    main()

import os, re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from denethor.core.database.conn import Connection
from datetime import datetime

SQL_FILES_PATH = "scripts/sql/instance_generator/"  # Diretório onde os arquivos SQL estão localizados
INSTANCE_FILE_PATH = "resources/data/instance_files/"  # Diretório onde os arquivos de instância serão salvos
WRITE_COMMENTS_TO_FILE = True

# Connect to the PostgreSQL database
session = Connection().get_session()

EXECUTION_MAPPING = {
    "2": {"aws_ec2": [124], "aws_lambda": [68, 69, 70, 71, 72]},
    "5": {"aws_ec2": [125], "aws_lambda": [73, 74, 75, 76, 77]},
    "10": {"aws_ec2": [126], "aws_lambda": [78, 79, 80, 81, 82]},
    "15": {"aws_ec2": [127], "aws_lambda": [84, 85, 86, 87, 88]},
    "20": {"aws_ec2": [128], "aws_lambda": [89, 90, 91, 92, 93]},
    "25": {"aws_ec2": [129], "aws_lambda": [94, 95, 96, 97, 98]},
    "30": {"aws_ec2": [130], "aws_lambda": [99, 100, 101, 102, 103]},
    "35": {"aws_ec2": [131], "aws_lambda": [104, 105, 106, 107, 108]},
    "40": {"aws_ec2": [132], "aws_lambda": [109, 110, 111, 112, 113]},
    "45": {"aws_ec2": [133], "aws_lambda": [114, 115, 116, 117, 118]},
    "50": {"aws_ec2": [134], "aws_lambda": [119, 120, 121, 122, 123]},
}


def main():

    for input_count, entry in EXECUTION_MAPPING.items():

        weids_fx = entry["aws_lambda"]
        weids_vm = entry["aws_ec2"]

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


if __name__ == "__main__":
    main()

import os, time, timeit
from denethor.core import denethor_logger as dlh
from denethor.utils import aws_utils as dau
import tree_constructor_core as tcc
from denethor.utils import file_utils as dfu, utils as du


def handler(event, context):

    start_time = timeit.default_timer()

    request_id = du.resolve_request_id(context)
    provider = event.get("provider")
    s3_bucket = event.get("bucket")
    s3_keys = event.get("keys")

    execution_tag = "file_metrics_tag_" + start_time

    local_path_files = "/tmp/files"
    local_path_logs = "/tmp/logs"
    log_file_name = f"{execution_tag}.log"

    dfu.create_directory_if_not_exists(local_path_files, local_path_logs)
    
    # Create a logger
    logger, log_file = dlh.get_simple_logger(log_file_name, local_path_files)

    logger.info(
        f"FILE_METRICS_START RequestId: {request_id}\t Provider: {provider} StartTime: {start_time} ExecutionTag: {execution_tag}" 
    )

    for s3_key in s3_keys:

        # List files from s3 bucket
        files = dau.list_files_in_s3(s3_bucket, s3_key)

        # Download files from s3 bucket
        dau.handle_consumed_files(
            request_id, provider, files, local_path_files, s3_bucket, s3_key, logger
        )

        # Uploaf files to s3 bucket
        s3_key_up = os.path.join("file_metrics", execution_tag, s3_key)
        dau.handle_produced_files(
            request_id, provider, files, local_path_files, s3_bucket, s3_key_up, logger
        )

    end_time = timeit.default_timer()
    logger.info(
        f"FILE_METRICS_END RequestId: {request_id}\t Provider: {provider} EndTime: {end_time} ExecutionTag: {execution_tag}"
    )
    logger.info(
        f"FILE_METRICS_DURATION RequestId: {request_id}\t Provider: {provider} Duration: {end_time - start_time} ms"
    )

    # Upload log file to s3 bucket
    log_file_name = os.path.basename(log_file)
    s3_key_log = os.path.join("file_metrics", execution_tag, log_file_name)
    dau.upload_single_file_to_s3(
        log_file_name, local_path_files, s3_bucket, s3_key_log
    )

    return {"request_id": request_id, "data": s3_key_log}

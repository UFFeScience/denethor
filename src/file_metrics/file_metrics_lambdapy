import os, time, timeit, json
from denethor.core import denethor_logger as dlh
from denethor.utils import file_utils as dfu, utils as du, aws_utils as dau


def handler(event, context):

    start_time_ms = timeit.default_timer()
    
    request_id = du.resolve_request_id(context)
    provider = event.get("provider")
    s3_bucket = event.get("bucket")
    s3_key = event.get("key")
    files = event.get("files")

    execution_tag = "file_metrics_tag_" + str(int(time.time() * 1000))

    local_path_files = "/tmp/files"
    local_path_logs = "/tmp/logs"
    log_file_name = f"{execution_tag}.log"

    dfu.create_directory_if_not_exists(local_path_files, local_path_logs)
    
    # Create a logger
    logger, log_file = dlh.get_simple_logger(log_file_name, local_path_files)

    logger.info(
        f"FILE_METRICS_START RequestId: {request_id}\t S3Key: {s3_key}\t Provider: {provider}\t StartTime: {start_time_ms} ms\t ExecutionTag: {execution_tag}" 
    )

    if not files:
        # List files from s3 bucket
        files = dau.list_files_in_s3(s3_bucket, s3_key)
    
    # Get files base names
    files = [os.path.basename(file) for file in files]

    # Download files from s3 bucket
    download_metrics = dau.handle_consumed_files(
        request_id, provider, files, local_path_files, s3_bucket, s3_key, logger
    )
    
    # Save download_metrics as JSON
    download_metrics_file = os.path.join(local_path_logs, f"{execution_tag}_download_metrics.json")
    with open(download_metrics_file, "w") as f:
        json.dump(download_metrics, f, indent=4)

    # Upload files to s3 bucket
    s3_key_up = os.path.join("file_metrics", s3_key)
    upload_metrics = dau.handle_produced_files(
        request_id, provider, files, local_path_files, s3_bucket, s3_key_up, logger
    )

    # Save upload_metrics as JSON
    upload_metrics_file = os.path.join(local_path_logs, f"{execution_tag}_upload_metrics.json")
    with open(upload_metrics_file, "w") as f:
        json.dump(upload_metrics, f, indent=4)

    end_time_ms = timeit.default_timer()
    logger.info(
        f"FILE_METRICS_END RequestId: {request_id}\t S3Key: {s3_key}\t Provider: {provider}\t EndTime: {end_time_ms} ms\t Duration: {end_time_ms - start_time_ms} ms\t ExecutionTag: {execution_tag}"
    )

    # Upload log file to s3 bucket
    log_file_name = os.path.basename(log_file)
    s3_key_log = "file_metrics"
    dau.upload_single_file_to_s3(
        log_file_name, local_path_files, s3_bucket, s3_key_log
    )

    # Upload metrics JSON files to s3 bucket
    dau.upload_single_file_to_s3(
        os.path.basename(download_metrics_file), local_path_logs, s3_bucket, s3_key_log
    )
    dau.upload_single_file_to_s3(
        os.path.basename(upload_metrics_file), local_path_logs, s3_bucket, s3_key_log
    )

    return {"request_id": request_id, "data": log_file_name}

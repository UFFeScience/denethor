import boto3
import timeit
import os
import datetime
import sys
import json

def download_files_and_collect_metrics(bucket_name, prefix, local_dir):
    """
    Downloads files from S3 and collects metrics for each file.
    Returns a list of metrics dicts and total duration.
    """
    s3 = boto3.client('s3')
    file_metrics = []
    start_time = timeit.default_timer()

    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                file_path = os.path.join(local_dir, key)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                download_start_time = timeit.default_timer()
                try:
                    s3.download_file(bucket_name, key, file_path)
                    download_end_time = timeit.default_timer()
                    file_size = os.path.getsize(file_path)
                    download_time = download_end_time - download_start_time

                    file_metrics.append({
                        "file_name": key,
                        "file_size": file_size,
                        "download_duration_ms": download_time * 1000
                    })
                except Exception as e:
                    print(f"Error downloading {key}: {e}")

    end_time = timeit.default_timer()
    total_duration = end_time - start_time
    return file_metrics, total_duration

def calculate_summary(file_metrics):
    """
    Calculates the summary dict from metrics and totals.
    """
    total_size_bytes = sum(f["file_size"] for f in file_metrics)
    total_duration_ms = sum(f["download_duration_ms"] for f in file_metrics)
    downloaded_count = len(file_metrics)
    average_duration_ms = total_duration_ms / downloaded_count if downloaded_count > 0 else 0
    average_rate_bps = (total_size_bytes * 8) / (total_duration_ms / 1000) if total_duration_ms > 0 else 0  # in bits per second
    return {
        "total_download_duration_ms": total_duration_ms,
        "total_files_size": total_size_bytes,
        "total_files_downloaded": downloaded_count,
        "average_download_duration_ms": average_duration_ms,
        "average_download_rate_bps": average_rate_bps,
        "files": file_metrics
    }

def save_json(data, path):
    """
    Saves data as JSON to the given path.
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def measure_download_rate_boto3(bucket_name, prefix, local_dir):
    print(f"Starting download from s3://{bucket_name}/{prefix}* to {local_dir}...")

    try:
        file_metrics, total_duration = download_files_and_collect_metrics(
            bucket_name, prefix, local_dir
        )

        summary = calculate_summary(file_metrics)

        # Unifica a saída em um único arquivo JSON
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = os.path.join(local_dir, f"download_report_{date_str}.json")
        json_data = {
            "summary": summary,
            "files": file_metrics
        }
        save_json(json_data, json_file)
        print(f"Relatório salvo em {json_file}")
        print("\n--- Download Summary ---")
        print(f"Total files downloaded: {summary['total_files_downloaded']}")
        print(f"Total size downloaded: {summary['total_files_size'] / (1024 * 1024):.2f} MB")
        print(f"Total download time: {summary['total_download_duration_ms'] / 1000:.2f} seconds")
        print(f"Average download rate: {summary['average_download_rate_bps'] / 1_000_000:.2f} Mbps")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 file_metrics_ec2.py <bucket_name> <s3_prefix> <local_dir>")
        sys.exit(1)

    bucket_name = sys.argv[1]
    prefix = sys.argv[2]
    local_dir = sys.argv[3]

    # Ensure the local directory exists
    os.makedirs(local_dir, exist_ok=True)

    measure_download_rate_boto3(bucket_name, prefix, local_dir)
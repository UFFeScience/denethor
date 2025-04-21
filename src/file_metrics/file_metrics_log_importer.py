import json
import os
import sys
from sqlalchemy.sql import text  # Import the text function

# Add the parent directory of 'denethor' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from denethor.core.database.conn import Connection  # Import the Connection class

# Round 1
# tags = ["tag_1745177128804", "tag_1745177624996", "tag_1745180172977"]

# Round 2
# tags = ["tag_1745185548987", "tag_1745185763146", "tag_1745185812164"]

# Round 3
tags = ["tag_1745186286839", "tag_1745186429082", "tag_1745186545767"]

# Define the metrics directory
metrics_dir = os.path.join(os.path.dirname(__file__), "logs")


def main():

    # Define the metrics directory
    metrics_dir = os.path.join(os.path.dirname(__file__), "logs")

    # Initialize database connection
    connection = Connection()

    # Process each tag
    for tag in tags:
        download_metrics_file = f"file_metrics_{tag}_download_metrics.json"
        upload_metrics_file = f"file_metrics_{tag}_upload_metrics.json"

        download_path = os.path.join(metrics_dir, download_metrics_file)
        print(f"Download path: {download_path}")

        upload_path = os.path.join(metrics_dir, upload_metrics_file)
        print(f"Upload path: {upload_path}")

        if os.path.exists(download_path) and os.path.exists(upload_path):
            # Read download metrics JSON
            with open(download_path, "r") as download_file:
                download_metrics = json.load(download_file)

            # Read upload metrics JSON
            with open(upload_path, "r") as upload_file:
                upload_metrics = json.load(upload_file)

            # Save metrics to the database
            save_metrics_to_db(tag, {"download_metrics": download_metrics["files"], "upload_metrics": upload_metrics["files"]}, connection)
        else:
            print(f"Metrics files for tag {tag} are incomplete or missing.")


def save_metrics_to_db(tag, metrics, connection):
    """
    Save metrics to the database.

    :param tag: The tag associated with the metrics.
    :param metrics: A dictionary containing download and upload metrics.
    :param connection: An instance of the Connection class.
    """
    session = None
    try:
        # Get a database session
        session = connection.get_session()

        # Insert download metrics
        for file in metrics["download_metrics"]:
            session.execute(
                text("""
                INSERT INTO file_metrics (tag, file_name, file_size, duration_ms, metric_type)
                VALUES (:tag, :file_name, :file_size, :duration_ms, :metric_type)
                """),
                {
                    "tag": tag,
                    "file_name": file["file_name"],
                    "file_size": file["file_size"],
                    "duration_ms": file["download_duration_ms"],
                    "metric_type": "download"
                }
            )
            print(f"Inserted download metric for file {file['file_name']} with size {file['file_size']} and duration {file['download_duration_ms']} ms.")

        # Insert upload metrics
        for file in metrics["upload_metrics"]:
            session.execute(
                text("""
                INSERT INTO file_metrics (tag, file_name, file_size, duration_ms, metric_type)
                VALUES (:tag, :file_name, :file_size, :duration_ms, :metric_type)
                """),
                {
                    "tag": tag,
                    "file_name": file["file_name"],
                    "file_size": file["file_size"],
                    "duration_ms": file["upload_duration_ms"],
                    "metric_type": "upload"
                }
            )
            print(f"Inserted upload metric for file {file['file_name']} with size {file['file_size']} and duration {file['upload_duration_ms']} ms.")

        # Commit the transaction
        session.commit()
        print(f"Metrics for tag {tag} successfully saved to the database.")

    except Exception as e:
        print(f"Error saving metrics for tag {tag} to the database: {e}")
        if session:
            session.rollback()
    finally:
        if session:
            session.close()


if __name__ == "__main__":
    main()

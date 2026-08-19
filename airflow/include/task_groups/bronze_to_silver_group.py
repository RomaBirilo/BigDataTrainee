from airflow.sdk import task_group
from airflow.include.tasks.bronze_to_silver_tasks import (resolve_source_prefix, list_bronze_filees,
                                                          download_bronze_files, upload_to_silver)

BUCKET_NAME = "weather-pipeline-datalake-dev-ce4e33"

@task_group(group_id="process_location")
def process_location(location: str, source_path: str | None = None):
    prefix = resolve_source_prefix(source_path=source_path, location=location)
    blobs = list_bronze_files(bucket_name=BUCKET_NAME, prefix=prefix)
    records = download_bronze_files(blobs=blobs, bucket_name=BUCKET_NAME, prefix=prefix)
    upload_to_silver(records=records, prefix=prefix, bucket_name=BUCKET_NAME)



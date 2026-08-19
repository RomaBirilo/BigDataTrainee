from airflow.sdk import task
from pendulum import now
from airflow.exceptions import AirflowFailException
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.include.validation.weather_validation import filter_valid_payloads, build_dataframe, deduplicate
from airflow.include.upload.serialize_to_csv import records_to_csv_bytes

@task
def resolve_source_prefix(source_path: str | None, location: str) -> str:
    if source_path:
        return source_path
    target_hour = pendulum.now("UTC").subtract(hours=1)
    return f"bronze/weather/realtime/{location}/{target_hour.format('YYYY/MM/DD/HH')}"

@task
def list_bronze_files(bucket_name: str, prefix: str) -> list[str]:
    hook = GCSHook()
    blobs = hook.list(bucket_name=bucket_name, prefix=prefix)
    return blobs

@task
def download_bronze_files(blobs: list[str], bucket_name: str, prefix: str) -> list[dict]:
    hook = GCSHook()
    json_blobs = [b for b in blobs if b.endswith(".json")]

    if not json_blobs:
        raise AirflowFailException(
            f"Validation failed: no .json files found in gcs://{bucket_name}/{prefix}."
        )

    ingested_at = pendulum.now("UTC").to_iso8601_string()
    raw_payloads = []
    for blob in json_blobs:
        payload = json.loads(hook.download(bucket_name=bucket_name, object_name=blob))
        payload["source_object"] = blob
        payload["ingested_at_utc"] = ingested_at
        payloads.append(payload)
        raw_payloads.append((payload, blob))

    valid_payloads, skipped = filter_valid_payloads(raw_payloads)
    if skipped:
        log.warning(f"Dropped {skipped}/{len(json_blobs)} invalid file(s) in gs://{bucket_name}/{prefix}")

    if not valid_payloads:
        raise AirflowFailException(
            f"Validation failed: no valid records remain after validation in gs://{bucket_name}/{prefix}."
        )

    df = build_dataframe(valid_payloads)
    df = deduplicate(df)

    if df.empty:
        raise AirflowFailException(
            f"Validation failed: no valid records remain after deduplication in gs://{bucket_name}/{prefix}."
        )

    return df.to_dict(orient="records")

@task
def upload_to_silver(records: list[dict], prefix: str, bucket_name: str) -> None:
    if not records:
        raise AirflowFailException("Cannot upload to silver: records list is empty.")
    prefix = prefix.replace("bronze", "silver")
    run_ts = pendulum.now("UTC").to_iso8601_string()

    object_name = prefix + f"/{run_ts}.csv"

    csv_bytes = records_to_csv_bytes(records)

    hook = GCSHook()
    hook.upload(
        bucket_name=bucket_name,
        object_name=object_name,
        data=csv_bytes,
        mime_type="text/csv",
    )
    log.info(f"Uploaded {len(records)} record(s) to gсs://{bucket_name}/{object_name}")
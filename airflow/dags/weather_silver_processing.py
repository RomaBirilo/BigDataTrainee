from pendulum import datetime
from airflow.sdk import dag
from include.task_groups.bronze_to_silver_group import process_location, BUCKET_NAME
from include.config.locations import LOCATIONS
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

PROJECT_ID = "project-5980accb-bff7-409b-9ee"

@dag(
    schedule=None,
    start_date=datetime(2025, 1, 1),
    tags=['weather-silver-processing'],
    catchup=False
)
def weather_silver_processing():
    silver_group = process_location.expand(location=LOCATIONS)

    load_to_bq = GCSToBigQueryOperator(
        task_id="load_silver_to_bigquery",
        bucket=BUCKET_NAME,
        source_objects=["silver/weather/realtime/*.csv"],
        destination_project_dataset_table=f"{PROJECT_ID}.weather_analytics.gold_weather_realtime",
        source_format="CSV",
        skip_leading_rows=1,
        write_disposition="WRITE_APPEND",
        schema_fields=[
            {"name": "event_time", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "location_lat", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "location_lon", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "location_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "location_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "source_object", "type": "STRING", "mode": "REQUIRED"},
            {"name": "ingested_at_utc", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "weather_humidity", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "weather_windSpeed", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "weather_cloudCover", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "weather_temperature", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "weather_precipitationProbability", "type": "FLOAT", "mode": "NULLABLE"},
        ],
        autodetect=False,
        gcp_conn_id="google_cloud_default",
    )

    silver_group >> load_to_bq

weather_silver_processing()
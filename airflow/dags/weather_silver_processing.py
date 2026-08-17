from pendulum import datetime, now
from airflow.sdk import dag, task
from airflow.exceptions import AirflowException, AirflowFailException
from airflow.providers.google.cloud.hooks.gcs import GCSHook
import json
import pandas as pd

@dag(
    schedule=None,
    start_date=datetime(2025, 1, 1),
    tags=['weather-silver-processing'],
    catchup=False
)
def weather_silver_processing():
    @task
    def resolve_source_prefix(source_path: str | None, location: str) -> str:
        if source_path:
            return source_path
        target_hour = pendulum.now("UTC").subtract(hours=1)
        return f"bronze/weather/realtime/{location}/{target_hour.format('YYYY/MM/DD/HH')}"

    @task
    def list_bronze_files(prefix: str) -> list[str]:
        hook = GCSHook()
        blobs = hook.list(bucket_name="weather-pipeline-datalake-dev-ce4e33", prefix=prefix)
        return blobs

    @task
    def download_bronze_files(blobs: list[str]) -> list[dict]:
        hook = GCSHook()
        payloads = [json.loads(hook.download(bucket_name="weather-pipeline-datalake-dev-ce4e33", obbject_name=file))
                    for file in blobs]
        if not payloads:
            raise AirflowFailException(f"Validation failed: in the {bucket_name} bucket at the {prefix_path} path "
                                       f"No .json files were found in the past hour. The pipeline has been stopped.")
        df = pd.json_normalize(payloads)
        df = df.rename(columns={
            "data.time": "event_time",
            "location.name": "location_name",
            "location.lat": "location_lat",
            "location.lon": "location_lon",
            "location.type": "location_type",
            "data.values.temperature": "weather_temperature",
            "data.values.humidity": "weather_humidity",
            "data.values.windSpeed": "weather_windSpeed",
            "data.values.cloudCover": "weather_cloudCover",
            "data.values.precipitationProbability": "weather_precipitationProbability",
        })
        return df.to_dict(orient="records")

    # @task
    # def check_json_structure(files_dict: list[dict]) -> None:
    #     for dct in files_dict:
    #         data_section = dct.get("data")
    #         location_section = dct.get("location")
    #         data_values_section = dct.get("data").get("values")
    #         if not data_section or not isinstance(data_section, dict):
    #             print("Structure validation failed: the ‘data’ section is missing or is not a dictionary.")
    #             continue
    #         if not location_section or not isinstance(data_section, dict):
    #             print("Structure validation failed: the ‘location’ section is missing or is not a dictionary.")
    #             continue
    #         if not data_values_section or not isinstance(data_section, dict):
    #             print("Structure validation failed: the ‘values’ section is missing or is not a dictionary.")
    #             continue
    # @task
    # def check_numeric_fields(files_dict: list[dict]) -> None:
    #     numeric_fields = ["temperature", "humidity", "windSpeed", "cloudCover", "precipitationProbability"]
    #     for dct in files_dict:
    #         for field in numeric_fields:
    #             if not isinstance(dct.get("data").get("values").get(field), float):
    #                 print(f"Structure validation failed: the {field} field is not numeric")
    #                 continue
    #
    # @task
    # def check_value_ranges(files_dict: list[dict]) -> None:
    #     numeric_fields = ["temperature", "humidity", "windSpeed", "cloudCover", "precipitationProbability"]
    #     for dct in files_dict:
    #         for field in numeric_fields:
    #             value = dct.get("data").get("values").get(field)
    #             if field == "temperature" and (value < -90 or value > 70):
    #                 print(f"Range validation failed: the {field} field out of range")
    #                 continue
    #             elif field == "windSpeed" and (value < 0 or value > 150):
    #                 print(f"Range validation failed: the {field} field out of range")
    #                 continue
    #             elif value < 0 or value > 100:
    #                 print(f"Range validation failed: the {field} field out of range")
    #                 continue
    #
    # @task
    # def deduplication(files_dict: list[dict]) -> None:
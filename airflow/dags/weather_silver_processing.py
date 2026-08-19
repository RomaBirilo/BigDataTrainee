from pendulum import datetime
from airflow.sdk import dag
from airflow.include.task_groups.bronze_to_silver_group import process_location

@dag(
    schedule=None,
    start_date=datetime(2025, 1, 1),
    tags=['weather-silver-processing'],
    catchup=False
)
def weather_silver_processing():
    pass
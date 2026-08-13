import json
import os
from datetime import datetime, timezone

import functions_framework
import requests
from google.cloud import secretmanager
from google.cloud import storage

PROJECT_ID = os.environ.get("PROJECT_ID")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
WEATHER_API_SECRET_ID = os.environ.get("WEATHER_API_SECRET_ID")
WEATHER_API_BASE_URL = os.environ.get(
    "WEATHER_API_BASE_URL", "https://api.tomorrow.io/v4/weather/realtime"
)
WEATHER_LOCATIONS = [
    loc.strip() for loc in os.environ.get("WEATHER_LOCATIONS", "").split(",") if loc.strip()
]

secret_client = secretmanager.SecretManagerServiceClient()
storage_client = storage.Client()


def get_api_key():
    name = f"projects/{PROJECT_ID}/secrets/{WEATHER_API_SECRET_ID}/versions/latest"
    response = secret_client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")


def fetch_weather(location, api_key):
    params = {"location": location, "apikey": api_key, "units": "metric"}
    response = requests.get(WEATHER_API_BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def write_to_gcs(location, payload):
    now = datetime.now(timezone.utc)
    safe_location = location.replace(" ", "_").replace(",", "")
    blob_path = (
        f"bronze/weather/realtime/{safe_location}/"
        f"{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}/{now.strftime('%H')}/"
        f"{now.strftime('%Y%m%dT%H%M%S')}Z.json"
    )
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(json.dumps(payload), content_type="application/json")
    return blob_path


@functions_framework.http
def main(request):
    if not WEATHER_LOCATIONS:
        return ("No locations configured", 500)

    api_key = get_api_key()
    written = []

    for location in WEATHER_LOCATIONS:
        payload = fetch_weather(location, api_key)
        blob_path = write_to_gcs(location, payload)
        written.append(blob_path)

    return (json.dumps({"written": written}), 200)
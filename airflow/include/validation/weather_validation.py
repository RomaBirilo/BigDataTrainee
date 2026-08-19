import json
import pandas as pd
import logging

log = logging.getLogger(__name__)

NUMERIC_RANGES = {
    "temperature": (-90, 70),
    "humidity": (0, 100),
    "windSpeed": (0, 150),
    "cloudCover": (0, 100),
    "precipitationProbability": (0, 100),
}

RENAME_MAP = {
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
}

TARGET_COLUMNS = [
    "source_object", "event_time", "location_name", "location_lat",
    "location_lon", "location_type", "ingested_at_utc",
    "weather_temperature", "weather_humidity", "weather_windSpeed",
    "weather_cloudCover", "weather_precipitationProbability",
]

def check_json_structure(payload: dict) -> str | None:
    if not isinstance(payload.get("data"), dict):
        return f"Validation failed: 'data' section missing or not a dict"
    if not isinstance(payload.get("location"), dict):
        return f"Validation failed: 'location' section missing or not a dict"

    values = payload["data"].get("values")
    if not isinstance(values, dict):
        return f"Validation failed: 'data.values' section missing or not a dict"

    return check_numeric_fields(values)

def check_numeric_fields(values: dict) -> str | None:
    for field, (low, high) in NUMERIC_RANGES.items():
        if field not in values:
            continue
        value = values[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return f"field '{field}' is not numeric (got {type(value).__name__})"
        if not (low <= value <= high):
            return f"field '{field}' out of range [{low}, {high}] (got {value})"
    return None

def filter_valid_payloads(raw_payloads: list[tuple[dict, str]],) -> tuple[list[dict], int]:
    valid = []
    skipped = 0
    for payload, blob in raw_payloads:
        reason = check_json_structure(payload)
        if reason is not None:
            log.warning(f"Dropping invalid record from {blob}: {reason}")
            skipped += 1
            continue
        valid.append(payload)
    return valid, skipped

def build_dataframe(payloads: list[dict]) -> pd.DataFrame:
    df = pd.json_normalize(payloads)
    df = df.rename(columns=RENAME_MAP)
    return df.reindex(columns=TARGET_COLUMNS)


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=["location_name", "event_time"], keep="first")
    dropped = before - len(df)
    if dropped:
        log.warning(f"Dropped {dropped} duplicate record(s) by (location_name, event_time)")
    return df
resource "google_bigquery_dataset" "weather" {
  project    = var.project_id
  dataset_id = var.bq_dataset_id
  location   = var.bq_location
  labels     = local.common_labels

  depends_on = [google_project_service.required]
}

resource "google_bigquery_table" "gold_weather" {
  project             = var.project_id
  dataset_id          = google_bigquery_dataset.weather.dataset_id
  table_id            = var.bq_table_id
  deletion_protection = var.bq_table_deletion_protection
  labels              = local.common_labels

  time_partitioning {
    type  = "DAY"
    field = "event_time"
  }

  clustering = ["location_name"]

  schema = jsonencode([
    {
      name        = "source_object"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "source path of file from where object came"
    },
    {
      name        = "event_time"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "value from time field"
    },
    {
      name = "location_name"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "location_lat"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "location_lon"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "location_type"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name        = "ingested_at_utc"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "timestamp where rows were processed"
    },
    {
      name = "weather_temperature"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "weather_humidity"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "weather_windSpeed"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "weather_cloudCover"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "weather_precipitationProbability"
      type = "FLOAT"
      mode = "NULLABLE"
    }
  ])
}

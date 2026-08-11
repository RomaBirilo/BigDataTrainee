output "data_lake_bucket_name" {
  value = google_storage_bucket.data_lake.name
}

output "function_source_bucket_name" {
  value = google_storage_bucket.function_source.name
}

output "function_name" {
  value = google_cloudfunctions2_function.weather_ingest.name
}

output "function_uri" {
  value = google_cloudfunctions2_function.weather_ingest.service_config[0].uri
}

output "weather_api_secret_id" {
  value = google_secret_manager_secret.weather_api_key.secret_id
}

output "weather_api_secret_add_version_command" {
  value = "gcloud secrets versions add ${google_secret_manager_secret.weather_api_key.secret_id} --project=${var.project_id} --data-file=-"
}

output "bq_dataset_id" {
  value = google_bigquery_dataset.weather.dataset_id
}

output "bq_table_id" {
  value = google_bigquery_table.gold_weather.table_id
}

output "function_service_account_email" {
  value = google_service_account.function_sa.email
}

output "scheduler_service_account_email" {
  value = google_service_account.scheduler_sa.email
}

output "airflow_service_account_email" {
  value = google_service_account.airflow_sa.email
}

output "airflow_impersonation_login_command" {
  value = "gcloud auth application-default login --impersonate-service-account=${google_service_account.airflow_sa.email}"
}

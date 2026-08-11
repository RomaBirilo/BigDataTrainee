resource "google_storage_bucket_iam_member" "function_sa_bronze_writer" {
  bucket = google_storage_bucket.data_lake.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.function_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "function_sa_secret_accessor" {
  secret_id = google_secret_manager_secret.weather_api_key.secret_id
  project   = var.project_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.function_sa.email}"
}

resource "google_cloudfunctions2_function_iam_member" "scheduler_invoker" {
  project        = var.project_id
  location       = var.region
  cloud_function = google_cloudfunctions2_function.weather_ingest.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

resource "google_cloud_run_service_iam_member" "scheduler_run_invoker" {
  project  = var.project_id
  location = var.region
  service  = google_cloudfunctions2_function.weather_ingest.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

resource "google_storage_bucket_iam_member" "airflow_sa_data_lake_admin" {
  bucket = google_storage_bucket.data_lake.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.airflow_sa.email}"
}

resource "google_bigquery_dataset_iam_member" "airflow_sa_dataset_editor" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.weather.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.airflow_sa.email}"
}

resource "google_project_iam_member" "airflow_sa_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.airflow_sa.email}"
}

data "google_client_openid_userinfo" "me" {
  count = var.airflow_operator_principal == "" ? 1 : 0
}

locals {
  airflow_operator_principal = var.airflow_operator_principal != "" ? var.airflow_operator_principal : "user:${data.google_client_openid_userinfo.me[0].email}"
}

resource "google_service_account_iam_member" "airflow_sa_token_creator" {
  service_account_id = google_service_account.airflow_sa.name
  role                = "roles/iam.serviceAccountTokenCreator"
  member              = local.airflow_operator_principal
}

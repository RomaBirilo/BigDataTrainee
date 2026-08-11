data "archive_file" "function_source" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/.build/function-source.zip"
}

resource "google_storage_bucket_object" "function_source" {
  name   = "source/${var.function_name}-${data.archive_file.function_source.output_md5}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.function_source.output_path
}

resource "google_cloudfunctions2_function" "weather_ingest" {
  project     = var.project_id
  name        = "${var.app_name}-${var.function_name}-${var.env}"
  location    = var.region
  description = "Fetches current weather from the source API and writes raw JSON to the bronze layer in GCS."

  build_config {
    runtime     = var.function_runtime
    entry_point = var.function_entry_point

    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_source.name
      }
    }
  }

  service_config {
    available_memory               = var.function_memory
    timeout_seconds                = var.function_timeout_seconds
    min_instance_count             = var.function_min_instance_count
    max_instance_count             = var.function_max_instance_count
    ingress_settings               = "ALLOW_ALL"
    all_traffic_on_latest_revision = true
    service_account_email          = google_service_account.function_sa.email

    environment_variables = {
      PROJECT_ID            = var.project_id
      BUCKET_NAME            = google_storage_bucket.data_lake.name
      WEATHER_API_SECRET_ID  = google_secret_manager_secret.weather_api_key.secret_id
      WEATHER_API_BASE_URL   = var.weather_api_base_url
      WEATHER_LOCATIONS      = join(",", var.weather_locations)
    }
  }

  labels = local.common_labels

  depends_on = [
    google_project_service.required,
    google_project_iam_member.cloudbuild_sa_builder,
    google_project_iam_member.compute_default_sa_builder,
  ]
}

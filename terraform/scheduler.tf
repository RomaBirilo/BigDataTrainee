resource "google_cloud_scheduler_job" "weather_ingest_trigger" {
  project   = var.project_id
  region    = var.region
  name      = "${var.app_name}-${var.function_name}-trigger-${var.env}"
  schedule  = var.scheduler_cron
  time_zone = var.scheduler_time_zone

  http_target {
    uri         = google_cloudfunctions2_function.weather_ingest.service_config[0].uri
    http_method = "POST"

    oidc_token {
      service_account_email = google_service_account.scheduler_sa.email
      audience               = google_cloudfunctions2_function.weather_ingest.service_config[0].uri
    }
  }

  retry_config {
    retry_count = 1
  }

  depends_on = [
    google_project_service.required,
    google_cloudfunctions2_function_iam_member.scheduler_invoker,
    google_cloud_run_service_iam_member.scheduler_run_invoker,
  ]
}

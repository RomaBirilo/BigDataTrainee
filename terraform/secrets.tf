resource "google_secret_manager_secret" "weather_api_key" {
  secret_id = var.weather_api_secret_id
  project   = var.project_id
  labels    = local.common_labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.required]
}

resource "google_service_account" "function_sa" {
  project      = var.project_id
  account_id   = "${substr(var.app_name, 0, 12)}-fn-${var.env}"
  display_name = "Weather ingest Cloud Function SA (${var.env})"
}

resource "google_service_account" "scheduler_sa" {
  project      = var.project_id
  account_id   = "${substr(var.app_name, 0, 12)}-sch-${var.env}"
  display_name = "Weather ingest Cloud Scheduler SA (${var.env})"
}

resource "google_service_account" "airflow_sa" {
  project      = var.project_id
  account_id   = "${substr(var.app_name, 0, 12)}-af-${var.env}"
  display_name = "Local Airflow processing SA (${var.env})"
}

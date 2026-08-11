locals {
  common_labels = merge(
    var.labels,
    {
      env     = var.env
      owner   = var.owner
      app     = var.app_name
      managed = "terraform"
    }
  )
}

resource "random_id" "suffix" {
  byte_length = 3
}

resource "google_storage_bucket" "data_lake" {
  name                        = "${var.app_name}-datalake-${var.env}-${random_id.suffix.hex}"
  project                     = var.project_id
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = var.bucket_force_destroy
  labels                      = local.common_labels

  versioning {
    enabled = var.bucket_versioning_enabled
  }

  depends_on = [google_project_service.required]
}

resource "google_storage_bucket" "function_source" {
  name                        = "${var.app_name}-fnsrc-${var.env}-${random_id.suffix.hex}"
  project                     = var.project_id
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
  labels                      = local.common_labels

  depends_on = [google_project_service.required]
}

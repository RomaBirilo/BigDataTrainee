variable "project_id" {
  type = string

  validation {
    condition     = length(var.project_id) > 0
    error_message = "project_id must not be empty."
  }
}

variable "region" {
  type    = string
  default = "us-central1"

  validation {
    condition     = length(var.region) > 0
    error_message = "region must not be empty."
  }
}

variable "env" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.env)
    error_message = "env must be one of: dev, staging, prod."
  }
}

variable "app_name" {
  type    = string
  default = "weather-pipeline"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.app_name))
    error_message = "app_name must be lowercase alphanumeric with dashes, 3-21 chars, starting with a letter."
  }
}

variable "owner" {
  type    = string
  default = "data-platform-team"
}

variable "labels" {
  type    = map(string)
  default = {}
}

variable "bucket_force_destroy" {
  type    = bool
  default = false
}

variable "bucket_versioning_enabled" {
  type    = bool
  default = true
}

variable "scheduler_cron" {
  type    = string
  default = "*/10 * * * *"

  validation {
    condition     = length(var.scheduler_cron) > 0
    error_message = "scheduler_cron must not be empty."
  }
}

variable "scheduler_time_zone" {
  type    = string
  default = "UTC"
}

variable "weather_api_secret_id" {
  type    = string
  default = "weather-api-key"

  validation {
    condition     = can(regex("^[a-zA-Z0-9_-]{1,255}$", var.weather_api_secret_id))
    error_message = "weather_api_secret_id must be a valid Secret Manager secret id."
  }
}

variable "weather_api_base_url" {
  type    = string
  default = "https://api.tomorrow.io/v4/weather/realtime"
}

variable "weather_locations" {
  type    = list(string)
  default = ["New York"]

  validation {
    condition     = length(var.weather_locations) > 0
    error_message = "weather_locations must contain at least one location."
  }
}

variable "bq_dataset_id" {
  type    = string
  default = "weather_analytics"
}

variable "bq_table_id" {
  type    = string
  default = "gold_weather_realtime"
}

variable "bq_location" {
  type    = string
  default = "US"
}

variable "bq_table_deletion_protection" {
  type    = bool
  default = true
}

variable "function_name" {
  type    = string
  default = "weather-ingest"
}

variable "function_entry_point" {
  type    = string
  default = "main"
}

variable "function_runtime" {
  type    = string
  default = "python312"
}

variable "function_memory" {
  type    = string
  default = "256Mi"
}

variable "function_timeout_seconds" {
  type    = number
  default = 60

  validation {
    condition     = var.function_timeout_seconds > 0 && var.function_timeout_seconds <= 540
    error_message = "function_timeout_seconds must be between 1 and 540."
  }
}

variable "function_min_instance_count" {
  type    = number
  default = 0
}

variable "function_max_instance_count" {
  type    = number
  default = 2
}

variable "airflow_operator_principal" {
  type    = string
  default = ""

  validation {
    condition     = var.airflow_operator_principal == "" || can(regex("^(user|serviceAccount|group):.+", var.airflow_operator_principal))
    error_message = "airflow_operator_principal must be empty, or start with user:, serviceAccount: or group:."
  }
}

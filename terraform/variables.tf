# This file contains detailed descriptions of all variables used in main.tf

variable "solution_name" {
  description = "Base name for all resources. Will be used as a prefix for resource naming."
  type        = string
  default     = "dataguardian"
}

variable "location" {
  description = "Azure region where resources will be created"
  type        = string
  default     = "westeurope"
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Environment must be one of: dev, test, prod."
  }
}

variable "admin_username" {
  description = "PostgreSQL admin username"
  type        = string
  default     = "dataguardian_admin"
}

variable "admin_password" {
  description = "PostgreSQL admin password. Must be at least 8 characters long and contain characters from three of the following categories: English uppercase letters, English lowercase letters, numbers (0-9), and non-alphanumeric characters."
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "DataGuardian Pro"
    Environment = "Development"
    Terraform   = "True"
  }
}

# Optional variables with defaults
variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "13"
}

variable "postgres_sku" {
  description = "PostgreSQL SKU name"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "webapp_sku" {
  description = "App Service Plan SKU"
  type        = string
  default     = "B1"
}

variable "enable_high_availability" {
  description = "Enable high availability for PostgreSQL (only for production)"
  type        = bool
  default     = false
}
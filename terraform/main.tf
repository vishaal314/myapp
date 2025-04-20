terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Create resource group
resource "azurerm_resource_group" "rg" {
  name     = "${var.solution_name}-${var.environment}-rg"
  location = var.location
  tags     = var.tags
}

# Create Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = "${var.solution_name}${var.environment}acr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
  tags                = var.tags
}

# Create PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = "${var.solution_name}-${var.environment}-db"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  version                = var.postgres_version
  administrator_login    = var.admin_username
  administrator_password = var.admin_password
  storage_mb             = 32768
  sku_name               = var.postgres_sku
  backup_retention_days  = 7
  tags                   = var.tags
  
  # Add high availability configuration if enabled
  dynamic "high_availability" {
    for_each = var.enable_high_availability ? [1] : []
    content {
      mode = "ZoneRedundant"
    }
  }
}

# Create the database
resource "azurerm_postgresql_flexible_server_database" "database" {
  name      = var.solution_name
  server_id = azurerm_postgresql_flexible_server.postgres.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Allow Azure services to access PostgreSQL
resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.postgres.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Create App Service Plan
resource "azurerm_service_plan" "app_plan" {
  name                = "${var.solution_name}-${var.environment}-plan"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = var.webapp_sku
  tags                = var.tags
}

# Create Web App for Containers
resource "azurerm_linux_web_app" "app" {
  name                = "${var.solution_name}-${var.environment}-app"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.app_plan.id
  https_only          = true
  tags                = var.tags

  site_config {
    always_on        = true
    ftps_state       = "Disabled"
    health_check_path = "/"

    application_stack {
      docker_image     = "${azurerm_container_registry.acr.login_server}/${var.solution_name}"
      docker_image_tag = "latest"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    DOCKER_REGISTRY_SERVER_URL          = "https://${azurerm_container_registry.acr.login_server}"
    DOCKER_REGISTRY_SERVER_USERNAME     = azurerm_container_registry.acr.admin_username
    DOCKER_REGISTRY_SERVER_PASSWORD     = azurerm_container_registry.acr.admin_password
    WEBSITES_PORT                       = "5000"
    PGHOST                              = azurerm_postgresql_flexible_server.postgres.fqdn
    PGDATABASE                          = azurerm_postgresql_flexible_server_database.database.name
    PGUSER                              = var.admin_username
    PGPASSWORD                          = var.admin_password
    PGPORT                              = "5432"
    DATABASE_URL                        = "postgresql://${var.admin_username}:${var.admin_password}@${azurerm_postgresql_flexible_server.postgres.fqdn}:5432/${azurerm_postgresql_flexible_server_database.database.name}"
  }

  logs {
    application_logs {
      file_system_level = "Information"
    }
    
    http_logs {
      file_system {
        retention_in_days = 7
        retention_in_mb   = 35
      }
    }
  }
  
  depends_on = [
    azurerm_container_registry.acr,
    azurerm_postgresql_flexible_server.postgres,
    azurerm_postgresql_flexible_server_database.database
  ]
}

# Grant the App Service access to ACR
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_linux_web_app.app.identity[0].principal_id
}

# Create Application Insights
resource "azurerm_application_insights" "insights" {
  name                = "${var.solution_name}-${var.environment}-insights"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
  tags                = var.tags
}

# Outputs
output "app_url" {
  value = "https://${azurerm_linux_web_app.app.default_hostname}"
}

output "postgresql_server_fqdn" {
  value = azurerm_postgresql_flexible_server.postgres.fqdn
}

output "container_registry_url" {
  value = azurerm_container_registry.acr.login_server
}

output "application_insights_instrumentation_key" {
  value     = azurerm_application_insights.insights.instrumentation_key
  sensitive = true
}
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.66.0"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Create a resource group
resource "azurerm_resource_group" "rg" {
  name     = "TaskTracker-RG"
  location = "westcentralus" # Had to use westcentralus because it is the only region with quota for B1 VMs for App Service Plan and PostgreSQL Flexible Server
}

# Create an Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = "TaskTrackerACR25"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

# Create an Azure App Service Plan
resource "azurerm_service_plan" "asp" {
  name                = "TaskTracker-ASP"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

# Create an Azure Linux Web App
resource "azurerm_linux_web_app" "alwa" {
  name                = "TaskTracker-ALWA"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.asp.id

  site_config {
    application_stack {
      docker_registry_url = "https://${azurerm_container_registry.acr.login_server}"
      docker_registry_username = azurerm_container_registry.acr.admin_username
      docker_registry_password = azurerm_container_registry.acr.admin_password
      docker_image_name = "task-tracker:latest"
    }
  }

  app_settings = { 
    "POSTGRES_HOST" = azurerm_postgresql_flexible_server.apfs.fqdn,
    "POSTGRES_PORT" = "5432",
    "POSTGRES_DB" = azurerm_postgresql_flexible_server_database.apfdb.name,
    "POSTGRES_USER" = azurerm_postgresql_flexible_server.apfs.administrator_login,
    "POSTGRES_PASSWORD" = var.postgresql_password,
    "WEBSITES_PORT" = "8000"
  }
}

# Create an Azure PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "apfs" {
  name                          = "tasktracker-apfs"
  resource_group_name           = azurerm_resource_group.rg.name
  location                      = azurerm_resource_group.rg.location
  version                       = "17"
  public_network_access_enabled = true
  administrator_login           = "tasktrackeradmin"
  administrator_password        = var.postgresql_password

  sku_name = "B_Standard_B1ms"
}

# Create a PostgreSQL database in the Flexible Server
resource "azurerm_postgresql_flexible_server_database" "apfdb" {
  name      = "task_tracker_db"
  server_id = azurerm_postgresql_flexible_server.apfs.id
  collation = "en_US.utf8"
  charset   = "UTF8"

  # lifecycle {
  #   prevent_destroy = false # If true, it wont be destroyed when running terraform destroy
  # }
}

# Create a firewall rule to allow access to the PostgreSQL Flexible Server from all IP addresses (for testing purposes)
resource "azurerm_postgresql_flexible_server_firewall_rule" "apfsfr" {
  name             = "TaskTracker-FW"
  server_id        = azurerm_postgresql_flexible_server.apfs.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}
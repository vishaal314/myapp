# Production environment configuration for DataGuardian Pro

environment = "prod"
location = "westeurope"  # Choose the appropriate region

# Higher tier for production workloads
postgres_sku = "GP_Standard_D2s_v3"
webapp_sku = "P1v2"

# Enable high availability for production
enable_high_availability = true

tags = {
  Project     = "DataGuardian Pro"
  Environment = "Production"
  Terraform   = "True"
  Owner       = "DataGuardian Team"
}
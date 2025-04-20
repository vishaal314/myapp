# Default values for DataGuardian Pro deployment
# You can override these by creating a terraform.tfvars.local file (which should be git-ignored)

solution_name = "dataguardian"
location = "westeurope"
environment = "dev"
admin_username = "dataguardian_admin"
# admin_password should be provided through environment variable TF_VAR_admin_password
# or in a gitignored terraform.tfvars.local file, NOT HERE

postgres_version = "13"
postgres_sku = "B_Standard_B1ms"
webapp_sku = "B1"
enable_high_availability = false

tags = {
  Project     = "DataGuardian Pro"
  Environment = "Development"
  Terraform   = "True"
  Owner       = "DataGuardian Team"
}
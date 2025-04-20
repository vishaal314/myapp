# DataGuardian Pro - Terraform Deployment

This directory contains Terraform configuration files to deploy DataGuardian Pro to Azure with a single command. The deployment includes all necessary infrastructure:

- PostgreSQL flexible server database
- Azure Container Registry for Docker images
- App Service Plan and Web App for Containers
- Application Insights for monitoring
- Network security and access configuration

## Prerequisites

Before deploying, ensure you have:

1. **Azure Account**: An active Azure subscription
2. **Terraform**: Installed locally (v1.0.0+)
3. **Azure CLI**: Installed and configured locally

## Quick Start Deployment

The simplest way to deploy is using the provided script:

```bash
cd terraform
./deploy.sh
```

This will:
1. Check prerequisites
2. Log you into Azure (if not already logged in)
3. Initialize Terraform
4. Show you the deployment plan (optional)
5. Deploy all resources to Azure
6. Output connection URLs and next steps

## Configuration Options

### Environment Selection

Choose which environment to deploy:

```bash
# Development environment (default)
./deploy.sh -e dev

# Testing environment
./deploy.sh -e test

# Production environment
./deploy.sh -e prod
```

Each environment uses different configuration values appropriate for that environment.

### Sensitive Information

The PostgreSQL admin password is required for deployment. You can provide it in one of these ways:

1. **Environment variable** (recommended):
   ```bash
   export TF_VAR_admin_password="YourStrongPassword123!"
   ./deploy.sh
   ```

2. **Local variables file**:
   Create a file named `terraform.tfvars.local` (gitignored) with:
   ```
   admin_password = "YourStrongPassword123!"
   ```

3. **Interactive prompt**:
   If neither of the above is provided, the script will prompt you for the password.

## Custom Configuration

You can customize deployment settings in several ways:

1. Edit `terraform.tfvars` for general configuration
2. Create environment-specific configurations (like `production.tfvars`)
3. Override any value via command line:
   ```bash
   terraform apply -var="solution_name=customname" -var="location=northeurope"
   ```

## Manual Deployment

If you prefer not to use the script, you can run Terraform commands directly:

```bash
# Initialize Terraform
terraform init

# See what will be created
terraform plan -var-file=production.tfvars -out=tfplan

# Apply the plan
terraform apply tfplan

# Or apply directly
terraform apply -var-file=production.tfvars
```

## Post-Deployment

After deployment completes:

1. Build your Docker image:
   ```bash
   docker build -t <acr-name>.azurecr.io/dataguardian:latest .
   ```

2. Log in to ACR:
   ```bash
   az acr login --name <acr-name>
   ```

3. Push your image:
   ```bash
   docker push <acr-name>.azurecr.io/dataguardian:latest
   ```

The web app will automatically pull and deploy the image.

## Destroying Infrastructure

To remove all resources when no longer needed:

```bash
terraform destroy
```

Review the plan carefully before confirming deletion.

## Troubleshooting

### Common Issues

1. **Terraform initialization fails**:
   Ensure you have connectivity to Azure and try running:
   ```bash
   terraform init -upgrade
   ```

2. **Permission errors**:
   Ensure your Azure account has the necessary roles:
   - Contributor role on the subscription or resource group
   - User Access Administrator to assign roles to the web app

3. **Deployment times out**:
   Azure resource creation can take time, especially PostgreSQL. Increase timeout or try again.

4. **Failed deployments**:
   If a deployment fails, run:
   ```bash
   terraform plan
   ```
   to see what changes need to be made and address any errors before trying again.

## Security Notes

- The PostgreSQL server allows Azure services by default, which is required for App Service connectivity
- All connections use TLS encryption
- For production, consider adding:
  - Azure Private Link for PostgreSQL
  - VNet integration for App Service
  - Advanced Threat Protection
  - Geo-redundant backups
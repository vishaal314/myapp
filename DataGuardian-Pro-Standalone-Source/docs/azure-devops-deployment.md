# Azure DevOps Deployment Guide for DataGuardian Pro

This guide provides detailed instructions for deploying DataGuardian Pro using Azure DevOps and Azure services.

## Overview

The deployment workflow will be:
1. Develop on Replit
2. Push changes to Azure DevOps repository
3. Azure DevOps Pipeline automatically builds and deploys to Azure App Service

## Prerequisites

- Azure subscription with active access
- Azure DevOps organization and project
- Replit account (for development)
- Basic familiarity with Git commands

## Step 1: Connect Replit to Azure DevOps

1. From your Replit project, run the provided script:
   ```bash
   ./scripts/connect-azure-devops.sh
   ```

2. Enter your Azure DevOps username and Personal Access Token (PAT) when prompted.
   - If you don't have a PAT, create one in Azure DevOps:
     - Go to User Settings (top right corner) > Personal Access Tokens
     - Click "New Token"
     - Name it "DataGuardian Deployment"
     - Set expiration as needed
     - For scope, select "Full access" or specifically "Code (Read & Write)" and "Build (Read & Execute)"
     - Click "Create" and copy the token

3. Follow the prompts to commit and push your code to the Azure DevOps repository.

## Step 2: Set Up Azure Resources

### Create Azure Container Registry (ACR)

1. In the Azure Portal, click "Create a resource"
2. Search for "Container Registry" and click "Create"
3. Fill in the basics:
   - Resource group: Create new, e.g., "dataguardian-rg"
   - Registry name: "dataguardianacr" (must be globally unique)
   - Location: Choose nearest to you
   - SKU: Basic
4. Click "Review + create" and then "Create"

### Create PostgreSQL Flexible Server

1. In the Azure Portal, click "Create a resource"
2. Search for "Azure Database for PostgreSQL flexible server" and click "Create"
3. Fill in the basics:
   - Resource group: Same as ACR
   - Server name: "dataguardian-db" (must be unique)
   - Region: Same as ACR
   - PostgreSQL version: 13
   - Workload type: Development
   - Compute + storage: Burstable B1ms (for dev/test)
4. On the Authentication tab:
   - Admin username: dataguardian
   - Password: (create a strong password)
5. Click "Review + create" and then "Create"

### Create a Database

1. Once the server is created, go to its resource page
2. In the left menu, click "Databases"
3. Click "Add" to create a new database
4. Enter "dataguardian" as the name and click "Save"

### Create App Service

1. In the Azure Portal, click "Create a resource"
2. Search for "Web App" and click "Create"
3. Fill in the basics:
   - Resource group: Same as ACR
   - Name: "dataguardian-app" (must be unique)
   - Publish: Docker Container
   - Operating System: Linux
   - Region: Same as ACR
   - App Service Plan: Create new, "dataguardian-plan" (B1 is sufficient for development)
4. On the Docker tab:
   - Options: Single Container
   - Image Source: Azure Container Registry
   - Registry: Select your ACR
   - Image: dataguardian-app
   - Tag: latest
5. Click "Review + create" and then "Create"

## Step 3: Set Up Azure DevOps Pipeline

1. Go to your Azure DevOps project
2. Click "Pipelines" > "New pipeline"
3. Select "Azure Repos Git" as the source
4. Select your repository
5. Select "Existing Azure Pipelines YAML file"
6. Select "/azure-pipelines.yml" from the dropdown
7. Click "Continue"
8. Review the pipeline and click "Save and run"

### Configure Pipeline Variables

1. Go to your pipeline in Azure DevOps
2. Click "Edit" and then click the "Variables" button
3. Add the following variables:
   - `resourceGroup`: Your resource group name (e.g., "dataguardian-rg")
   - `pgHost`: Your PostgreSQL server hostname (e.g., "dataguardian-db.postgres.database.azure.com")
   - `pgUser`: Your PostgreSQL username (e.g., "dataguardian")
   - `pgPassword`: Your PostgreSQL password (mark as secret)
   - `pgDatabase`: Your PostgreSQL database name (e.g., "dataguardian")
   - `runDatabaseSetup`: "true" for first run, "false" after that

### Create Service Connections

1. In your Azure DevOps project, go to "Project settings" (bottom left corner)
2. Under "Pipelines", click "Service connections"
3. Click "New service connection" and create the following:

#### Azure Container Registry Connection
1. Select "Docker Registry"
2. Registry type: Azure Container Registry
3. Subscription: Select your Azure subscription
4. Azure container registry: Select your ACR
5. Service connection name: "dataguardian-acr"
6. Click "Save"

#### Azure Service Connection
1. Click "New service connection" again
2. Select "Azure Resource Manager"
3. Authentication method: Service principal (automatic)
4. Scope level: Subscription
5. Subscription: Select your Azure subscription
6. Resource Group: Your resource group
7. Service connection name: "dataguardian-azure-connection"
8. Click "Save"

## Step 4: Deploy Your Application

1. The first time your pipeline runs, it will:
   - Build your Docker image
   - Push it to Azure Container Registry
   - Deploy it to Azure App Service
   - Configure environment variables
   - Initialize the database (if runDatabaseSetup is true)

2. Subsequent code changes pushed to your Azure DevOps repository will automatically trigger the pipeline.

3. Access your application at: https://dataguardian-app.azurewebsites.net

## Step 5: Configure Firewall Rules for PostgreSQL

1. Go to your PostgreSQL server in the Azure Portal
2. Click "Networking" in the left menu
3. Under "Firewall rules", add the following:
   - Rule name: "AppService"
   - Start IP: 0.0.0.0
   - End IP: 0.0.0.0
   - This allows Azure services to access your database
4. Click "Save"

## Development Workflow

Once everything is set up, your development workflow will be:

1. **Make changes in Replit**
   - Test your changes locally in Replit

2. **Push to Azure DevOps**
   - From Replit terminal:
     ```bash
     git add .
     git commit -m "Your commit message"
     git push
     ```
   - Or run the connection script again:
     ```bash
     ./scripts/connect-azure-devops.sh
     ```

3. **Monitor Deployment**
   - Go to your Azure DevOps project
   - Click "Pipelines" to see the build and deployment progress

4. **View Your App**
   - Go to https://dataguardian-app.azurewebsites.net after deployment completes

## Troubleshooting

### Pipeline Failures

1. Check the pipeline logs in Azure DevOps for detailed error messages.
2. Common issues include:
   - Service connection permissions
   - Docker build errors
   - Database connectivity issues

### Database Connectivity

If the application cannot connect to the database:

1. Check that the PostgreSQL server firewall rules allow Azure services
2. Verify the connection settings in the App Service Configuration
3. Try connecting to the database manually to confirm credentials:
   ```bash
   psql -h <your-db-server>.postgres.database.azure.com -U dataguardian -d dataguardian
   ```

### Docker Image Issues

If there are issues with the Docker image:

1. Try building it locally:
   ```bash
   docker build -t dataguardian-app:local .
   ```
2. Check for any errors in the Dockerfile

### App Service Logs

To check application logs:

1. Go to your App Service in the Azure Portal
2. Click "Log stream" in the left menu to see real-time logs
3. Or click "Advanced Tools" > "Go" > "LogFiles" to browse log files

## Scaling Up

When you're ready to move to production:

1. **Scale up the App Service Plan**:
   - Go to your App Service Plan in the Azure Portal
   - Click "Scale up (App Service Plan)" in the left menu
   - Select a P1v2 or higher tier for production workloads

2. **Scale up the PostgreSQL server**:
   - Go to your PostgreSQL server
   - Click "Compute + storage"
   - Select a more powerful tier

3. **Set up SSL**:
   - Go to your App Service
   - Click "Custom domains" in the left menu
   - Add your custom domain
   - Click "TLS/SSL settings" to add a certificate

## Security Best Practices

1. **Store secrets securely**:
   - Use pipeline variables marked as secret
   - Consider using Azure Key Vault for production

2. **Regular updates**:
   - Keep your Docker base image updated
   - Update packages regularly

3. **Network security**:
   - Restrict access to your PostgreSQL server
   - Use private endpoints in production

4. **Monitoring**:
   - Set up Azure Monitor alerts
   - Configure Application Insights for your App Service
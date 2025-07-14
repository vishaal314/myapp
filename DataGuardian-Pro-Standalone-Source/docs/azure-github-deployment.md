# Azure Deployment Guide with GitHub Integration

This guide provides step-by-step instructions for deploying DataGuardian Pro to Azure using GitHub and Replit for development.

## Overview

The deployment workflow will be:
1. Develop on Replit
2. Push changes to GitHub
3. Azure automatically deploys from GitHub (CI/CD)

## Prerequisites

- Azure account with active subscription
- GitHub account
- Replit account (for development)
- Basic familiarity with Git commands

## Step 1: Set Up GitHub Repository

1. Create a new GitHub repository:
   - Go to [GitHub](https://github.com)
   - Click "New repository" 
   - Name it "dataguardian-pro"
   - Choose public or private visibility
   - Click "Create repository"

2. Configure Replit to connect to GitHub:
   - In your Replit project, click on the Version Control icon in the sidebar
   - Click "Connect to GitHub"
   - Authenticate with GitHub
   - Select your "dataguardian-pro" repository
   - Click "Connect"

3. Push your code from Replit to GitHub:
   - In the Replit Version Control panel, add a commit message
   - Click "Commit & push"
   - Verify your code is now on GitHub

## Step 2: Set Up Azure App Service

1. Create an App Service in Azure:
   - Log in to [Azure Portal](https://portal.azure.com)
   - Click "Create a resource"
   - Search for "Web App" and select it
   - Click "Create"
   - Fill in the details:
     - Resource Group: Create new, e.g., "dataguardian-rg"
     - Name: "dataguardian-app"
     - Publish: "Docker Container"
     - Operating System: "Linux"
     - Region: Choose nearest to you
     - App Service Plan: Create new, e.g., "dataguardian-plan" (B1 or higher)
   - Click "Next: Docker"
   - Select "Single Container"
   - Image Source: "GitHub Actions (Preview)"
   - Click "Next: GitHub Actions" 
   - Authenticate with GitHub if needed
   - Select your repository and branch
   - Click "Review + create"
   - Click "Create"

## Step 3: Create Azure Database for PostgreSQL

1. Create a PostgreSQL server:
   - Go to Azure Portal
   - Click "Create a resource"
   - Search for "Azure Database for PostgreSQL"
   - Select "Flexible server" and click "Create"
   - Fill in the details:
     - Resource Group: Same as App Service (e.g., "dataguardian-rg")
     - Server name: "dataguardian-db"
     - Region: Same as App Service
     - Version: "13" or higher
     - Workload type: "Development"
     - Compute + storage: "Burstable" (B1ms for development)
     - Administrator username: "dataguardian"
     - Password: Create a secure password
   - Click "Next: Networking"
   - Access type: "Public access"
   - Add your IP address for development
   - Click "Review + create"
   - Click "Create"

2. Create a database:
   - Once the server is created, go to its resource page
   - In the left menu, click "Databases"
   - Click "Add"
   - Database name: "dataguardian"
   - Click "Save"

3. Initialize the database:
   - Go to "Connection security" in the left menu
   - Enable "Allow access to Azure services"
   - Add your client IP address
   - Click "Save"
   - Use psql or Azure Cloud Shell to run your database initialization script:
   ```bash
   psql "host=dataguardian-db.postgres.database.azure.com port=5432 dbname=dataguardian user=dataguardian password=<your-password> sslmode=require" -f database/postgres-init.sql
   ```

## Step 4: Configure GitHub Actions for CI/CD

1. GitHub will automatically create a workflow file, but you can customize it. Create a file at `.github/workflows/azure-deploy.yml` in your repository with:

```yaml
name: Build and deploy to Azure

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v1

    - name: Log in to registry
      uses: docker/login-action@v1
      with:
        registry: https://${{ secrets.REGISTRY_URL }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}

    - name: Build and push
      uses: docker/build-push-action@v2
      with:
        push: true
        tags: ${{ secrets.REGISTRY_URL }}/dataguardian-app:${{ github.sha }}
        file: ./Dockerfile
        context: .

  deploy:
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: 'production'
      url: ${{ steps.deploy-to-webapp.outputs.webapp-url }}

    steps:
    - name: Deploy to Azure Web App
      id: deploy-to-webapp
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'dataguardian-app'
        slot-name: 'production'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
        images: ${{ secrets.REGISTRY_URL }}/dataguardian-app:${{ github.sha }}
```

2. Configure GitHub repository secrets:
   - Go to your GitHub repository
   - Click "Settings" > "Secrets" > "Actions"
   - Add the following secrets (you'll get these from Azure):
     - `REGISTRY_URL`: The URL of your Azure Container Registry
     - `REGISTRY_USERNAME`: Username for your Azure Container Registry
     - `REGISTRY_PASSWORD`: Password for your Azure Container Registry
     - `AZURE_WEBAPP_PUBLISH_PROFILE`: The publish profile from your Azure Web App

## Step 5: Configure Azure Web App Environment

1. Set up environment variables in Azure:
   - Go to your App Service in Azure Portal
   - Click "Configuration" in the left menu
   - Under "Application settings", click "New application setting"
   - Add the following settings:
     - `PGHOST`: Your PostgreSQL server hostname (e.g., dataguardian-db.postgres.database.azure.com)
     - `PGUSER`: Your PostgreSQL username (e.g., dataguardian)
     - `PGPASSWORD`: Your PostgreSQL password
     - `PGDATABASE`: Your PostgreSQL database name (e.g., dataguardian)
     - `PGPORT`: 5432
     - `DATABASE_URL`: Full PostgreSQL connection string
     - `OPENAI_API_KEY`: Your OpenAI API key (if needed)
     - `STRIPE_SECRET_KEY`: Your Stripe secret key (if needed)
     - `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key (if needed)
   - Click "Save"

## Step 6: Replit to GitHub to Azure Workflow

Now you have a complete CI/CD pipeline:

1. **Development on Replit**:
   - Make changes to your code in Replit
   - Test your changes locally on Replit

2. **Push to GitHub**:
   - From Replit's Version Control panel, commit and push changes
   - Or run these commands in Replit Shell:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push
   ```

3. **Automatic Deployment to Azure**:
   - GitHub Actions will automatically detect the push
   - It will build a Docker image and push it to Azure Container Registry
   - It will deploy the updated image to your Azure App Service
   - You can monitor the deployment in the "Actions" tab of your GitHub repository

4. **Access Your App**:
   - Once deployment is complete, access your app at:
   - `https://dataguardian-app.azurewebsites.net`

## Additional Configuration

### Custom Domain

1. Add a custom domain:
   - Go to your App Service in Azure Portal
   - Click "Custom domains" in the left menu
   - Click "Add custom domain"
   - Follow the instructions to set up your domain

### Enable SSL

1. Configure SSL:
   - After setting up your custom domain
   - Go to "TLS/SSL settings" in the left menu
   - Click "Private Key Certificates" > "Create App Service Managed Certificate"
   - Select your custom domain
   - Click "Create"
   - Go back to "TLS/SSL settings"
   - Under "SSL bindings", click "Add SSL binding"
   - Select your custom domain and certificate
   - Set "TLS/SSL Type" to "SNI SSL"
   - Click "Add binding"

### Scaling Up

1. Scale up for production:
   - Go to your App Service Plan
   - Click "Scale up (App Service plan)" in the left menu
   - Select a larger tier (P1v2 or higher for production)
   - Click "Apply"

## Monitoring and Logs

1. Access logs:
   - Go to your App Service
   - Click "Log stream" to view real-time logs
   - Or click "App Service logs" to configure more detailed logging

2. Set up monitoring:
   - Click "Application Insights" for detailed monitoring
   - Click "Enable" if not already enabled
   - Click "View Application Insights data" to see metrics, performance data, and errors

## Troubleshooting

### Deployment Issues

1. Check GitHub Actions logs:
   - Go to your GitHub repository
   - Click the "Actions" tab
   - Click on the most recent workflow run
   - Review the logs for errors

2. Check Azure deployment logs:
   - Go to your App Service in Azure Portal
   - Click "Deployment Center" in the left menu
   - Review the deployment logs

### Database Connection Issues

1. Verify firewall rules:
   - Go to your PostgreSQL server
   - Click "Connection security"
   - Make sure "Allow access to Azure services" is ON
   - Verify your App Service IP is allowed

2. Check environment variables:
   - Go to your App Service
   - Click "Configuration"
   - Verify all database-related environment variables are correct
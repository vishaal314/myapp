#!/bin/bash

# Script to help set up Azure resources for DataGuardian Pro

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "======================================================"
echo "        Azure Setup for DataGuardian Pro              "
echo "======================================================"
echo -e "${NC}"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed.${NC}"
    echo -e "Please install Azure CLI first: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure
echo -e "${YELLOW}Logging in to Azure...${NC}"
az login
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to log in to Azure.${NC}"
    exit 1
fi

# Set subscription
echo -e "${YELLOW}Listing available subscriptions:${NC}"
az account list --output table

echo -e "${YELLOW}Enter the subscription ID to use:${NC}"
read -r subscription_id
az account set --subscription "$subscription_id"
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to set subscription.${NC}"
    exit 1
fi
echo -e "${GREEN}Subscription set successfully.${NC}"

# Set variables
echo -e "${YELLOW}Please enter a name for the resource group:${NC}"
read -r resource_group_name

echo -e "${YELLOW}Please enter a location (e.g., eastus, westeurope):${NC}"
read -r location

echo -e "${YELLOW}Please enter a name for the DataGuardian app:${NC}"
read -r app_name

echo -e "${YELLOW}Please enter a name for the PostgreSQL server:${NC}"
read -r db_server_name

echo -e "${YELLOW}Please enter a name for the PostgreSQL database:${NC}"
read -r db_name

echo -e "${YELLOW}Please enter a username for the PostgreSQL server:${NC}"
read -r admin_username

echo -e "${YELLOW}Please enter a password for the PostgreSQL server:${NC}"
read -rs admin_password
echo

# Create resource group
echo -e "${YELLOW}Creating resource group...${NC}"
az group create --name "$resource_group_name" --location "$location"
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create resource group.${NC}"
    exit 1
fi
echo -e "${GREEN}Resource group created successfully.${NC}"

# Create PostgreSQL server
echo -e "${YELLOW}Creating PostgreSQL server...${NC}"
az postgres flexible-server create \
    --resource-group "$resource_group_name" \
    --name "$db_server_name" \
    --location "$location" \
    --admin-user "$admin_username" \
    --admin-password "$admin_password" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 13
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create PostgreSQL server.${NC}"
    exit 1
fi
echo -e "${GREEN}PostgreSQL server created successfully.${NC}"

# Create PostgreSQL database
echo -e "${YELLOW}Creating PostgreSQL database...${NC}"
az postgres flexible-server db create \
    --resource-group "$resource_group_name" \
    --server-name "$db_server_name" \
    --database-name "$db_name"
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create PostgreSQL database.${NC}"
    exit 1
fi
echo -e "${GREEN}PostgreSQL database created successfully.${NC}"

# Create Azure Container Registry
echo -e "${YELLOW}Creating Azure Container Registry...${NC}"
acr_name="${app_name}acr"
# Remove any hyphens from ACR name as they're not allowed
acr_name=$(echo "$acr_name" | tr -d '-')
az acr create \
    --resource-group "$resource_group_name" \
    --name "$acr_name" \
    --sku Basic \
    --admin-enabled true
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create Azure Container Registry.${NC}"
    exit 1
fi
echo -e "${GREEN}Azure Container Registry created successfully.${NC}"

# Get ACR credentials
acr_username=$(az acr credential show --name "$acr_name" --resource-group "$resource_group_name" --query username --output tsv)
acr_password=$(az acr credential show --name "$acr_name" --resource-group "$resource_group_name" --query "passwords[0].value" --output tsv)
acr_url="${acr_name}.azurecr.io"

# Create App Service Plan
echo -e "${YELLOW}Creating App Service Plan...${NC}"
az appservice plan create \
    --resource-group "$resource_group_name" \
    --name "${app_name}-plan" \
    --is-linux \
    --sku B1
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create App Service Plan.${NC}"
    exit 1
fi
echo -e "${GREEN}App Service Plan created successfully.${NC}"

# Create Web App
echo -e "${YELLOW}Creating Web App...${NC}"
az webapp create \
    --resource-group "$resource_group_name" \
    --plan "${app_name}-plan" \
    --name "$app_name" \
    --deployment-container-image-name "${acr_url}/dataguardian-app:latest"
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create Web App.${NC}"
    exit 1
fi
echo -e "${GREEN}Web App created successfully.${NC}"

# Configure Web App
echo -e "${YELLOW}Configuring Web App...${NC}"
az webapp config appsettings set \
    --resource-group "$resource_group_name" \
    --name "$app_name" \
    --settings \
    PGHOST="${db_server_name}.postgres.database.azure.com" \
    PGUSER="${admin_username}" \
    PGPASSWORD="${admin_password}" \
    PGDATABASE="${db_name}" \
    PGPORT=5432 \
    DATABASE_URL="postgresql://${admin_username}:${admin_password}@${db_server_name}.postgres.database.azure.com:5432/${db_name}" \
    WEBSITES_PORT=5000
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to configure Web App.${NC}"
    exit 1
fi
echo -e "${GREEN}Web App configured successfully.${NC}"

# Get publish profile
echo -e "${YELLOW}Getting publish profile...${NC}"
publish_profile=$(az webapp deployment list-publishing-profiles --resource-group "$resource_group_name" --name "$app_name" --xml)
echo -e "${GREEN}Publish profile retrieved.${NC}"

# Output GitHub secrets
echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}Azure setup complete!${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo -e "${YELLOW}Add the following secrets to your GitHub repository:${NC}"
echo -e "REGISTRY_URL: ${acr_url}"
echo -e "REGISTRY_USERNAME: ${acr_username}"
echo -e "REGISTRY_PASSWORD: ${acr_password}"
echo -e "AZURE_WEBAPP_PUBLISH_PROFILE: <publish profile XML>"
echo -e "PGHOST: ${db_server_name}.postgres.database.azure.com"
echo -e "PGUSER: ${admin_username}"
echo -e "PGPASSWORD: ${admin_password}"
echo -e "PGDATABASE: ${db_name}"
echo -e "${BLUE}=====================================================${NC}"

# Ask if user wants to save the publish profile to a file
echo -e "${YELLOW}Do you want to save the publish profile to a file? [y/N]${NC}"
read -r save_profile
if [[ "$save_profile" =~ ^[Yy]$ ]]; then
    echo "$publish_profile" > "publish-profile.xml"
    echo -e "${GREEN}Publish profile saved to publish-profile.xml${NC}"
    echo -e "${YELLOW}IMPORTANT: This file contains sensitive information. Don't commit it to your repository.${NC}"
fi

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}Next Steps:${NC}"
echo -e "1. Create a GitHub repository and push your code"
echo -e "2. Add the secrets to your GitHub repository"
echo -e "3. Configure firewall to allow Azure services and your IP"
echo -e "4. Run a GitHub Actions workflow to deploy your app"
echo -e "${BLUE}=====================================================${NC}"

exit 0
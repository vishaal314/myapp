#!/bin/bash

# DataGuardian Pro Azure Deployment Script
# This script makes it easier to deploy DataGuardian Pro to Azure using Terraform

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "======================================================"
echo "    DataGuardian Pro Azure Deployment with Terraform  "
echo "======================================================"
echo -e "${NC}"

# Check if running in correct directory
if [ ! -f "main.tf" ]; then
    echo -e "${RED}Error: This script must be run from the terraform directory.${NC}"
    echo -e "${YELLOW}Change to the terraform directory and try again:${NC}"
    echo -e "  cd terraform"
    echo -e "  ./deploy.sh"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: Terraform is not installed.${NC}"
    echo -e "${YELLOW}Please install Terraform first:${NC}"
    echo -e "  https://learn.hashicorp.com/tutorials/terraform/install-cli"
    exit 1
fi

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed.${NC}"
    echo -e "${YELLOW}Please install Azure CLI first:${NC}"
    echo -e "  https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Set default environment
ENVIRONMENT="dev"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -e|--environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --init-only)
      INIT_ONLY=true
      shift
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|test|prod)$ ]]; then
    echo -e "${RED}Error: Invalid environment. Must be 'dev', 'test', or 'prod'.${NC}"
    exit 1
fi

# Determine var file to use
VAR_FILE=""
if [ "$ENVIRONMENT" == "prod" ]; then
    VAR_FILE="-var-file=production.tfvars"
    echo -e "${YELLOW}Using production configuration.${NC}"
elif [ "$ENVIRONMENT" == "test" ]; then
    VAR_FILE="-var-file=testing.tfvars"
    echo -e "${YELLOW}Using testing configuration.${NC}"
else
    echo -e "${YELLOW}Using development configuration.${NC}"
    # Default tfvars file will be used automatically
fi

# Check for local variable file (for secrets)
if [ -f "terraform.tfvars.local" ]; then
    LOCAL_VAR_FILE="-var-file=terraform.tfvars.local"
    echo -e "${GREEN}Using local variable file for sensitive values.${NC}"
else
    LOCAL_VAR_FILE=""
    echo -e "${YELLOW}Warning: No terraform.tfvars.local file found. Make sure to provide admin_password via environment variable or when prompted.${NC}"
fi

# Check if admin_password is set
if [ -z "$TF_VAR_admin_password" ]; then
    echo -e "${YELLOW}Admin password not set via environment variable.${NC}"
    
    # Only prompt if no local var file
    if [ -z "$LOCAL_VAR_FILE" ]; then
        echo -e "${YELLOW}Please enter PostgreSQL admin password:${NC}"
        read -s TF_VAR_admin_password
        export TF_VAR_admin_password
        echo
    fi
fi

# Login to Azure if needed
echo -e "${BLUE}Checking Azure login status...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Not logged in to Azure. Starting login process...${NC}"
    az login
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Azure login failed. Please try again.${NC}"
        exit 1
    fi
fi

# Display subscription
SUBSCRIPTION=$(az account show --query name -o tsv)
echo -e "${GREEN}Using Azure subscription: ${SUBSCRIPTION}${NC}"

# Initialize Terraform
echo -e "${BLUE}Initializing Terraform...${NC}"
terraform init

if [ $? -ne 0 ]; then
    echo -e "${RED}Terraform initialization failed.${NC}"
    exit 1
fi

# Exit if init only
if [ "$INIT_ONLY" = true ]; then
    echo -e "${GREEN}Terraform initialization completed successfully. Exiting as requested.${NC}"
    exit 0
fi

# Ask user if they want to see the plan first
echo -e "${YELLOW}Do you want to see the Terraform plan before applying? [Y/n]${NC}"
read see_plan
if [[ "$see_plan" =~ ^[Nn]$ ]]; then
    SKIP_PLAN=true
else
    SKIP_PLAN=false
fi

# Create plan
if [ "$SKIP_PLAN" = false ]; then
    echo -e "${BLUE}Creating Terraform plan...${NC}"
    terraform plan $VAR_FILE $LOCAL_VAR_FILE -out=tfplan
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Terraform plan creation failed.${NC}"
        exit 1
    fi
    
    # Ask for confirmation
    echo -e "${YELLOW}Do you want to apply this plan? [y/N]${NC}"
    read apply_plan
    if [[ ! "$apply_plan" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Deployment cancelled.${NC}"
        exit 0
    fi
    
    # Apply plan
    echo -e "${BLUE}Applying Terraform plan...${NC}"
    terraform apply tfplan
else
    # Apply directly
    echo -e "${BLUE}Applying Terraform configuration...${NC}"
    terraform apply -auto-approve $VAR_FILE $LOCAL_VAR_FILE
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}Terraform apply failed.${NC}"
    exit 1
fi

# Show outputs
echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}DataGuardian Pro deployment completed successfully!${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo -e "${YELLOW}App URL:${NC}"
terraform output app_url
echo -e "${YELLOW}PostgreSQL Server:${NC}"
terraform output postgresql_server_fqdn
echo -e "${YELLOW}Container Registry:${NC}"
terraform output container_registry_url
echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}Next Steps:${NC}"
echo -e "1. Build and push your Docker container to the Azure Container Registry"
echo -e "2. The app will automatically deploy once the container is available"
echo -e "3. Database is already set up and ready to use"
echo -e "${BLUE}=====================================================${NC}"

exit 0
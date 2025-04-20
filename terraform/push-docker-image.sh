#!/bin/bash

# Script to build and push Docker image to Azure Container Registry

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "======================================================"
echo "    DataGuardian Pro - Docker Image Build & Push      "
echo "======================================================"
echo -e "${NC}"

# Check if running in correct directory structure
if [ ! -f "../Dockerfile" ]; then
    echo -e "${RED}Error: This script must be run from the terraform directory with a Dockerfile in the parent directory.${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo -e "${YELLOW}Please install Docker first:${NC}"
    echo -e "  https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if az CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed.${NC}"
    echo -e "${YELLOW}Please install Azure CLI first:${NC}"
    echo -e "  https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Not logged in to Azure. Starting login process...${NC}"
    az login
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Azure login failed. Please try again.${NC}"
        exit 1
    fi
fi

# Get ACR info from Terraform output
echo -e "${BLUE}Getting ACR information from Terraform state...${NC}"
if ! terraform output -json &> /dev/null; then
    echo -e "${RED}Error: Could not get Terraform output. Make sure you have deployed the infrastructure first.${NC}"
    echo -e "${YELLOW}Run ./deploy.sh first, then try again.${NC}"
    exit 1
fi

ACR_URL=$(terraform output -raw container_registry_url)
if [ -z "$ACR_URL" ]; then
    echo -e "${RED}Error: Could not get ACR URL from Terraform output.${NC}"
    echo -e "${YELLOW}Make sure you have successfully deployed the infrastructure.${NC}"
    exit 1
fi

echo -e "${GREEN}Found ACR: ${ACR_URL}${NC}"

# Use solution name from ACR URL
SOLUTION_NAME=$(echo $ACR_URL | cut -d'.' -f1)
if [[ $SOLUTION_NAME == *acr ]]; then
    # Remove acr suffix if present
    SOLUTION_NAME=${SOLUTION_NAME%acr}
fi

# Check if no solution name could be extracted
if [ -z "$SOLUTION_NAME" ]; then
    echo -e "${YELLOW}Could not extract solution name from ACR URL. Using 'dataguardian' as default.${NC}"
    SOLUTION_NAME="dataguardian"
fi

IMAGE_NAME="${ACR_URL}/${SOLUTION_NAME}"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${BLUE}Will build and push image: ${FULL_IMAGE_NAME}${NC}"

# Ask for confirmation
echo -e "${YELLOW}Do you want to proceed with building and pushing the image? [y/N]${NC}"
read proceed
if [[ ! "$proceed" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Operation cancelled.${NC}"
    exit 0
fi

# Log in to ACR
echo -e "${BLUE}Logging in to Azure Container Registry...${NC}"
ACR_NAME=${ACR_URL%%.*}  # Extract name before first dot
az acr login --name $ACR_NAME

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to log in to ACR. Check your permissions and try again.${NC}"
    exit 1
fi

# Build Docker image
echo -e "${BLUE}Building Docker image...${NC}"
cd ..  # Go to parent directory where Dockerfile is
docker build -t $FULL_IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker build failed. Check the errors above and fix your Dockerfile.${NC}"
    exit 1
fi

# Push Docker image
echo -e "${BLUE}Pushing Docker image to ${ACR_URL}...${NC}"
docker push $FULL_IMAGE_NAME

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to push Docker image. Check your permissions and try again.${NC}"
    exit 1
fi

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}Docker image successfully built and pushed!${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo -e "${YELLOW}Image:${NC} ${FULL_IMAGE_NAME}"
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. The Azure App Service will automatically pull and deploy the new image"
echo -e "2. It may take a few minutes for the deployment to complete"
echo -e "3. Access your application at:"
terraform output -raw app_url
echo -e "${BLUE}=====================================================${NC}"

exit 0
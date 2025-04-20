#!/bin/bash

# Script to help connect your Replit project to Azure DevOps repository

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "======================================================"
echo "    Connect DataGuardian Pro to Azure DevOps Repo     "
echo "======================================================"
echo -e "${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: Git is not installed.${NC}"
    exit 1
fi

# Check if current directory is a git repository
if [ ! -d .git ]; then
    echo -e "${YELLOW}Initializing git repository...${NC}"
    git init
    echo -e "${GREEN}Git repository initialized.${NC}"
fi

# Pre-filled Azure DevOps details
azure_devops_org="vishaal786"
azure_devops_project="bankdesign"
azure_devops_repo="gdpr-scan-engine"
echo -e "${GREEN}Using Azure DevOps Organization: ${azure_devops_org}${NC}"
echo -e "${GREEN}Using Azure DevOps Project: ${azure_devops_project}${NC}"
echo -e "${GREEN}Using Azure DevOps Repository: ${azure_devops_repo}${NC}"

# Prompt for Azure DevOps credentials
echo -e "${YELLOW}Please enter your Azure DevOps username:${NC}"
read -r azure_devops_username

echo -e "${YELLOW}Please enter your Azure DevOps Personal Access Token (PAT):${NC}"
read -rs azure_devops_pat
echo

# Check if remote origin exists
remote_url="https://${azure_devops_username}:${azure_devops_pat}@dev.azure.com/${azure_devops_org}/${azure_devops_project}/_git/${azure_devops_repo}"

if git remote | grep -q "origin"; then
    echo -e "${YELLOW}Remote 'origin' already exists. Do you want to update it? [y/N]${NC}"
    read -r update_remote
    if [[ "$update_remote" =~ ^[Yy]$ ]]; then
        git remote set-url origin "$remote_url"
        echo -e "${GREEN}Remote origin updated.${NC}"
    fi
else
    git remote add origin "$remote_url"
    echo -e "${GREEN}Remote origin added.${NC}"
fi

# Ask if user wants to commit changes
echo -e "${YELLOW}Do you want to commit all changes? [y/N]${NC}"
read -r commit_changes
if [[ "$commit_changes" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Enter commit message:${NC}"
    read -r commit_message
    
    git add .
    git commit -m "$commit_message"
    echo -e "${GREEN}Changes committed.${NC}"
fi

# Ask if user wants to push to Azure DevOps
echo -e "${YELLOW}Do you want to push to Azure DevOps repository? [y/N]${NC}"
read -r push_repo
if [[ "$push_repo" =~ ^[Yy]$ ]]; then
    # Check if branch exists
    if ! git rev-parse --verify main &> /dev/null; then
        git branch -M main
    fi
    
    git push -u origin main
    echo -e "${GREEN}Changes pushed to Azure DevOps repository.${NC}"
fi

# Provide information about Azure deployment
echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}Azure DevOps Setup Complete!${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo -e "${YELLOW}Next Steps for Azure Deployment:${NC}"
echo -e "1. Create an Azure App Service (Web App) with Docker support"
echo -e "2. Set up Azure DevOps Pipeline for CI/CD"
echo -e "3. Configure environment variables in the Azure App Service"
echo -e "4. Create an Azure Database for PostgreSQL"
echo -e ""
echo -e "For detailed instructions, see ${BLUE}docs/azure-devops-deployment.md${NC}"
echo -e "${BLUE}=====================================================${NC}"

exit 0
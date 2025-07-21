#!/bin/bash

# Script to help connect your Replit project to GitHub and set up Azure deployment

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "======================================================"
echo "      Connect DataGuardian Pro to GitHub & Azure       "
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

# Pre-filled GitHub username
github_username="example_user"
echo -e "${GREEN}Using GitHub username: ${github_username}${NC}"

# Prompt for GitHub repository name
echo -e "${YELLOW}Please enter your GitHub repository name (e.g., dataguardian-pro):${NC}"
read -r github_repo

# Check if remote origin exists
if git remote | grep -q "origin"; then
    echo -e "${YELLOW}Remote 'origin' already exists. Do you want to update it? [y/N]${NC}"
    read -r update_remote
    if [[ "$update_remote" =~ ^[Yy]$ ]]; then
        git remote set-url origin "https://github.com/${github_username}/${github_repo}.git"
        echo -e "${GREEN}Remote origin updated.${NC}"
    fi
else
    git remote add origin "https://github.com/${github_username}/${github_repo}.git"
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

# Ask if user wants to push to GitHub
echo -e "${YELLOW}Do you want to push to GitHub? [y/N]${NC}"
read -r push_github
if [[ "$push_github" =~ ^[Yy]$ ]]; then
    # Check if branch exists
    if ! git rev-parse --verify main &> /dev/null; then
        git branch -M main
    fi
    
    git push -u origin main
    echo -e "${GREEN}Changes pushed to GitHub.${NC}"
fi

# Provide information about Azure deployment
echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}GitHub Setup Complete!${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo -e "${YELLOW}Next Steps for Azure Deployment:${NC}"
echo -e "1. Create an Azure App Service (Web App) with Docker support"
echo -e "2. Set up GitHub Actions for CI/CD:"
echo -e "   - Use the workflow file at .github/workflows/azure-deploy.yml"
echo -e "3. Set up secrets in your GitHub repository:"
echo -e "   - REGISTRY_URL"
echo -e "   - REGISTRY_USERNAME"
echo -e "   - REGISTRY_PASSWORD"
echo -e "   - AZURE_WEBAPP_PUBLISH_PROFILE"
echo -e "   - PGHOST, PGUSER, PGPASSWORD, PGDATABASE"
echo -e "4. Create an Azure Database for PostgreSQL"
echo -e ""
echo -e "For detailed instructions, see ${BLUE}docs/azure-github-deployment.md${NC}"
echo -e "${BLUE}=====================================================${NC}"

exit 0
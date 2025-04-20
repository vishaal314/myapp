#!/bin/bash

# DataGuardian Pro Deployment Script
# This script helps to deploy the DataGuardian Pro application using Docker Compose

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "======================================================"
echo "            DataGuardian Pro Deployment               "
echo "======================================================"
echo -e "${NC}"

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo "Please install Docker before running this script."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    echo "Please install Docker Compose before running this script."
    echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
    exit 1
fi

# Check if .env file exists, if not create it from example
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}Created .env file. Please edit it with your configuration.${NC}"
        echo -e "${YELLOW}Do you want to edit the .env file now? [y/N]${NC}"
        read -r edit_env
        if [[ "$edit_env" =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo -e "${RED}Error: .env.example not found.${NC}"
        exit 1
    fi
fi

# Make sure directories exist
mkdir -p reports uploads

# Offer to pull latest changes
echo -e "${YELLOW}Do you want to pull the latest changes from the repository? [y/N]${NC}"
read -r pull_latest
if [[ "$pull_latest" =~ ^[Yy]$ ]]; then
    git pull
    echo -e "${GREEN}Repository updated to the latest version.${NC}"
fi

# Run docker-compose build and up
echo -e "${BLUE}Building and starting DataGuardian Pro services...${NC}"
docker-compose build
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Docker build failed. See above for details.${NC}"
    exit 1
fi

# Start the services
echo -e "${BLUE}Starting services...${NC}"
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to start services. See above for details.${NC}"
    exit 1
fi

# Check if services are running
echo -e "${BLUE}Checking service status...${NC}"
sleep 5
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}Services are running!${NC}"
    
    # Get host IP
    HOST_IP=$(hostname -I | awk '{print $1}')
    APP_PORT=$(grep APP_PORT .env 2>/dev/null | cut -d '=' -f2 || echo 5000)
    
    echo -e "${GREEN}======================================================${NC}"
    echo -e "${GREEN}DataGuardian Pro is now running!${NC}"
    echo -e "${GREEN}Access the application at:${NC}"
    echo -e "${BLUE}http://localhost:${APP_PORT}${NC} (Local access)"
    echo -e "${BLUE}http://${HOST_IP}:${APP_PORT}${NC} (Network access)"
    echo -e "${GREEN}======================================================${NC}"
    echo ""
    echo -e "${YELLOW}To stop the application:${NC} docker-compose down"
    echo -e "${YELLOW}To view logs:${NC} docker-compose logs -f"
else
    echo -e "${RED}Error: Services failed to start properly.${NC}"
    echo "Check the logs with: docker-compose logs"
    exit 1
fi

exit 0
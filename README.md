# DataGuardian Pro - Enterprise Privacy Compliance Platform

DataGuardian Pro is a comprehensive enterprise privacy compliance platform designed to detect, analyze, and report on personally identifiable information (PII) across multiple data sources. With specialized focus on GDPR compliance, particularly Dutch implementation (UAVG), it provides organizations with the tools needed to maintain data privacy compliance.

![DataGuardian Pro Logo](generated-icon.png)

## Development and Deployment Workflow

DataGuardian Pro supports multiple development and deployment workflows:

### Option 1: Replit → Azure DevOps → Azure (Recommended)

1. **Development on Replit**: Write and test code in Replit's collaborative environment
2. **Version Control with Azure DevOps**: Push changes to Azure DevOps repository
3. **Automated Deployment to Azure**: Azure DevOps Pipeline automatically deploys changes to Azure

To get started with this workflow:

```bash
# Connect to Azure DevOps from Replit
./scripts/connect-azure-devops.sh
```

For detailed instructions, see [Azure DevOps Deployment Guide](docs/azure-devops-deployment.md)

### Option 2: Replit → GitHub → Azure

1. **Development on Replit**: Write and test code in Replit's collaborative environment
2. **Version Control with GitHub**: Push changes to GitHub for version control
3. **Automated Deployment to Azure**: GitHub Actions automatically deploys changes to Azure

To get started with this workflow:

```bash
# Connect to GitHub from Replit
./scripts/connect-github.sh

# Set up Azure resources (requires Azure CLI)
./scripts/azure-setup.sh
```

For detailed instructions, see [Azure GitHub Deployment Guide](docs/azure-github-deployment.md)

## Features

- **Multi-Service Scanning Engine**: Scan code, PDFs, images, databases, APIs, websites, and AI models
- **Intelligent Risk Analysis**: Smart AI-powered risk severity assessment
- **Comprehensive Reporting**: Detailed multilingual PDF and HTML reports
- **Internationalization**: Full support for English and Dutch languages
- **Role-Based Access Control**: Enterprise-grade security with 7 predefined roles
- **Modularity**: Scalable cloud-native architecture
- **Compliance Focus**: Built specifically for GDPR/UAVG requirements

## Technical Stack

- **Frontend**: Streamlit interactive web interface
- **Database**: PostgreSQL for storing scan results and configuration
- **Backend**: Python with specialized scanning services
- **Containerization**: Docker and Docker Compose for easy deployment
- **Security**: Advanced authentication and authorization
- **Language Support**: Native multilingual capabilities

## Deployment Options

### Local Docker Deployment

The easiest way to deploy DataGuardian Pro is using the provided Docker Compose configuration:

1. Ensure Docker and Docker Compose are installed on your system
2. Clone this repository
3. Run the deployment script:
   ```
   ./deploy.sh
   ```
4. Access the application at http://localhost:5000

### Manual Deployment

For manual deployment:

1. Clone this repository
2. Create and configure `.env` file (use `.env.example` as a template)
3. Build and start the containers:
   ```
   docker-compose build
   docker-compose up -d
   ```
4. Access the application at http://localhost:5000

### Cloud Deployment

DataGuardian Pro can be deployed to any cloud provider that supports Docker containers:

- **Azure**: Use Azure Container Instances or Azure Kubernetes Service
- **AWS**: Use ECS, EKS, or Elastic Beanstalk
- **GCP**: Use Google Kubernetes Engine or Cloud Run

## Configuration

Configure the application through the `.env` file:

- Database credentials
- Application port
- API keys for external services
- Debug and environment settings

## Usage

1. **Login**: Use default credentials (admin/password) for first-time login
2. **Select Scan Type**: Choose from code, document, image, database, API, website, or AI model scanning
3. **Configure Scan**: Set parameters specific to your scan type
4. **Run Scan**: Execute and view real-time progress
5. **Review Results**: Analyze findings in the dashboard
6. **Generate Reports**: Create PDF or HTML reports in your preferred language

## Scanner Types

- **Code Scanner**: Detects PII, credentials, and sensitive data in source code
- **Blob Scanner**: Finds PII in documents (PDFs, Word files, etc.)
- **Image Scanner**: Identifies PII in images using OCR and AI
- **Database Scanner**: Locates PII in database systems (PostgreSQL, MySQL, SQLite)
- **API Scanner**: Tests APIs for privacy and security issues
- **Website Scanner**: Crawls websites to discover PII and compliance issues
- **AI Model Scanner**: Evaluates AI models for data protection compliance

## Development

### Directory Structure

- `/app.py`: Main application entry point
- `/services/`: Individual scanning services
- `/utils/`: Utility functions and helpers
- `/translations/`: Language files
- `/database/`: Database schema and initialization files

### Adding a New Scanner

1. Create a new scanner class in the `/services/` directory
2. Implement the standard scanner interface
3. Add UI components in `app.py`
4. Update result aggregation logic
5. Add translations for new scanner elements

## License

Copyright © 2025 DataGuardian Pro - All rights reserved.
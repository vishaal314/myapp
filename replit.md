# DataGuardian Pro - Enterprise Privacy Compliance Platform

## Overview

DataGuardian Pro is a comprehensive enterprise privacy compliance platform built with Streamlit that detects, analyzes, and reports on personally identifiable information (PII) across multiple data sources. The application provides AI-powered risk assessment, multilingual support, and comprehensive reporting capabilities for GDPR and privacy compliance.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application
- **Language Support**: Internationalization with English and Dutch translations
- **Authentication**: Role-based access control with 7 predefined user roles
- **UI Components**: Modular design with reusable components and animated language switcher

### Backend Architecture
- **Language**: Python 3.11
- **Database**: PostgreSQL 16 (configurable via Drizzle ORM compatibility)
- **Containerization**: Docker with multi-stage builds
- **Deployment**: Support for Azure DevOps and GitHub workflows

## Key Components

### Core Scanning Services
1. **Code Scanner** (`services/code_scanner.py`) - Scans source code for security vulnerabilities and PII
2. **Blob Scanner** (`services/blob_scanner.py`) - Analyzes documents (PDF, DOCX, TXT) for PII detection
3. **Image Scanner** (`services/image_scanner.py`) - OCR-based PII detection in images
4. **Website Scanner** (`services/website_scanner.py`) - Web scraping and analysis for privacy compliance
5. **Database Scanner** (`services/db_scanner.py`) - Direct database scanning for PII across multiple DB types
6. **DPIA Scanner** (`services/dpia_scanner.py`) - Data Protection Impact Assessment automation
7. **AI Model Scanner** (`services/ai_model_scanner.py`) - AI/ML model privacy compliance analysis
8. **SOC2 Scanner** (`services/soc2_scanner.py`) - SOC2 compliance validation
9. **Sustainability Scanner** (`utils/scanners/sustainability_scanner.py`) - Environmental impact analysis

### Risk Analysis Engine
- **Smart Risk Analyzer** (`utils/risk_analyzer.py`) - AI-powered severity assessment
- **Regional Compliance** (`utils/gdpr_rules.py`) - Region-specific GDPR rules (Netherlands, Germany, France, Belgium)
- **Netherlands-specific GDPR** (`utils/netherlands_gdpr.py`) - UAVG compliance detection including BSN validation

### Report Generation
- **Multi-format Reports**: PDF and HTML report generation with professional styling
- **Certificate Generation** (`services/certificate_generator.py`) - Compliance certificates
- **Results Aggregation** (`services/results_aggregator.py`) - Centralized result processing and storage

### Authentication & Authorization
- **User Management** (`services/auth.py`) - Authentication with role-based permissions
- **Payment Integration** (`services/stripe_payment.py`) - Stripe integration for premium features

## Data Flow

1. **Input Sources**: Code repositories, documents, images, websites, databases
2. **Processing Pipeline**: 
   - Content extraction and preprocessing
   - PII pattern matching and detection
   - Risk severity analysis
   - Compliance validation
3. **Results Storage**: PostgreSQL database with scan history and findings
4. **Report Generation**: Professional PDF/HTML reports with actionable insights
5. **Delivery**: Download-ready reports with compliance certificates

## External Dependencies

### Core Dependencies
- **Streamlit**: Web application framework (>=1.44.1)
- **PostgreSQL**: Primary database (psycopg2-binary >=2.9.10)
- **OpenAI**: AI-powered analysis (>=1.75.0)
- **Stripe**: Payment processing (>=12.0.0)

### Document Processing
- **TextRact**: Document text extraction (>=1.6.5)
- **PyPDF2**: PDF processing (>=3.0.1)
- **ReportLab**: PDF report generation (>=4.4.0)
- **Pillow**: Image processing (>=11.2.1)

### Data Analysis (Note: Currently disabled due to numpy conflicts)
- **Pandas**: Data manipulation (>=2.2.3)
- **Plotly**: Interactive visualizations (>=6.1.2)
- **Matplotlib**: Static plotting

### Web Scraping & Analysis
- **BeautifulSoup4**: HTML parsing (>=4.8.2)
- **Requests**: HTTP client (>=2.32.3)
- **Trafilatura**: Web content extraction (>=2.0.0)
- **TLDExtract**: Domain analysis (>=5.2.0)

## Deployment Strategy

### Container Deployment
- **Dockerfile**: Multi-stage build with system dependencies (OCR, document processing)
- **Docker Compose**: Full stack deployment with Traefik reverse proxy and PostgreSQL
- **Health Checks**: Database connectivity and service availability monitoring

### Cloud Deployment Options
1. **Azure DevOps → Azure**: Recommended enterprise workflow
   - Azure Container Registry integration
   - Azure App Service deployment
   - Automated CI/CD pipeline
2. **GitHub → Azure**: Alternative workflow with GitHub Actions
3. **Replit**: Development and testing environment

### Environment Configuration
- **Environment Variables**: Centralized configuration via .env files
- **SSL/TLS**: Automatic certificate provisioning via Let's Encrypt
- **Scaling**: Autoscale deployment target configured

### Database Setup
- **PostgreSQL**: Primary database with initialization scripts
- **Schema Management**: Database schema definitions in `database/` directory
- **Connection Pooling**: Production-ready database connections

## Changelog
- June 23, 2025. Initial setup
- June 23, 2025. Implemented comprehensive Netherlands DPIA Assessment system with PostgreSQL database integration and HTML report generation

## Recent Changes
- Fixed duplicate button key issues in main application
- Removed Netherlands DPIA assessment section from main interface per user request
- Added new Simple DPIA Assessment feature with yes/no questions and digital signature
- Implemented instant HTML report generation for quick assessments
- Both comprehensive and simple DPIA options now available in main interface

## User Preferences

Preferred communication style: Simple, everyday language.
Interface preferences: Clean interface without additional assessment sections on main landing page.
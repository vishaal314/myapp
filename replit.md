# DataGuardian Pro - Enterprise Privacy Compliance Platform

## Overview
DataGuardian Pro is a comprehensive enterprise privacy compliance platform built with Streamlit that detects, analyzes, and reports on personally identifiable information (PII) across multiple data sources. The application provides AI-powered risk assessment, multilingual support, and comprehensive reporting capabilities for GDPR and privacy compliance, specifically targeting the Netherlands market with UAVG compliance. It aims to achieve €25K MRR from 100 customers through enhanced premium pricing strategy, offering 70-80% cost savings versus OneTrust with enterprise-grade features and Netherlands-specific compliance (UAVG, BSN detection, EU AI Act 2025).

## Recent Changes (August 3, 2025)
- **Netherlands Region Localization**: Fixed all report generators to default to "Netherlands" instead of "Global" for region compliance targeting Netherlands market
- **Language Switching Fix**: Resolved dashboard language switching issue where Dutch translations weren't loading when switching from English
- **Enhanced Dutch Translations**: Added missing dashboard translation keys for cost savings, performance, and sustainability metrics
- **Report Region Standardization**: Updated all PDF, HTML, and certificate generators to specify Netherlands as default compliance region

## User Preferences
Preferred communication style: Simple, everyday language.
Interface preferences: Clean interface without additional assessment sections on main landing page.
Data residency requirement: Netherlands/EU only hosting for GDPR compliance.
Deployment preference: Dutch hosting providers for complete data sovereignty.

## System Architecture
### Frontend Architecture
- **Framework**: Streamlit-based web application.
- **Language Support**: Internationalization with English and Dutch translations, including automated browser language detection.
- **Authentication**: Role-based access control with 7 predefined user roles, using bcrypt for password hashing and JWT for token authentication.
- **UI Components**: Modular design with reusable components, animated language switcher, professional styling, and a 6-tab settings system.

### Backend Architecture
- **Language**: Python 3.11.
- **Database**: PostgreSQL 16 (configurable via Drizzle ORM compatibility) with connection pooling and schema management.
- **Containerization**: Docker with multi-stage builds and Docker Compose for full-stack deployment.
- **Deployment**: Support for Azure DevOps, GitHub workflows, and local deployments.
- **Core Scanning Services**: Includes Code, Blob, Image (OCR-based), Website, Database, DPIA, AI Model, SOC2, and Sustainability scanners.
- **Risk Analysis Engine**: AI-powered Smart Risk Analyzer for severity assessment and region-specific GDPR rules (Netherlands, Germany, France, Belgium).
- **Report Generation**: Multi-format (PDF, HTML) report generation with professional styling, certificate generation, and centralized results aggregation.
- **Performance Optimization**: Redis caching layer, optimized database operations, async processing, and session isolation for multi-user concurrency.
- **Security**: Enterprise-grade security with environmental variable-based configuration for credentials, rate limiting, and comprehensive exception handling.

### Technical Implementations
- **Cost Savings Integration**: Comprehensive financial analysis across all 6 scanner types calculating GDPR penalty exposure (€50K-€20M), implementation costs, 3-year ROI (1,711%-14,518%), and OneTrust comparison showing 95%+ cost savings. Total value demonstrated: €43M+ in compliance savings.
- **AI Act Calculator**: Integrated 4-step wizard interface for EU AI Act 2025 compliance, including risk classification, Netherlands-specific features, and professional report generation.
- **License System**: Fully operational license management with usage tracking, revenue protection, and tier-based access control for all scanner types.
- **Activity Tracking**: Comprehensive user activity logging across all scanner functions for real-time dashboard metrics and audit trails.
- **Compliance Calculator**: Centralized compliance scoring logic with configurable regional penalties, advanced caching, and audit trail logging.
- **Intelligent Risk Analyzer**: ML-powered risk assessment with industry benchmarking and Netherlands UAVG compliance multipliers.
- **Automated Remediation Engine**: Semi-automated fix generation with Netherlands-specific BSN and cookie consent templates.
- **Advanced AI Scanner**: EU AI Act 2025 compliance with bias detection, explainability assessment, and penalty estimation.
- **Predictive Compliance Engine**: Machine learning-powered compliance forecasting with 85% accuracy and early warning system.
- **DPIA Implementation**: 5-step wizard interface for GDPR Article 35 compliance with real risk calculation and enhanced HTML reports.
- **Cookie & Tracking Compliance**: Comprehensive detection of consent banners, trackers, dark patterns, and privacy policy analysis per Netherlands AP rules.
- **Code Scanner**: Comprehensive PII detection (including BSN, health data, API keys), Netherlands UAVG compliance, and GDPR principles assessment.
- **Sustainability Scanner**: Zombie resource detection, regional CO₂ emission calculation, code bloat analysis, and professional reporting.

## External Dependencies
- **Streamlit**: Web application framework.
- **PostgreSQL**: Primary database.
- **OpenAI**: AI-powered analysis.
- **Stripe**: Payment processing.
- **TextRact**: Document text extraction.
- **PyPDF2**: PDF processing.
- **ReportLab**: PDF report generation.
- **Pillow**: Image processing.
- **BeautifulSoup4**: HTML parsing.
- **Requests**: HTTP client.
- **Trafilatura**: Web content extraction.
- **TLDExtract**: Domain analysis.
- **pytesseract**: OCR functionality for image scanning.
- **opencv-python-headless**: Image processing for OCR.
- **bcrypt**: Password hashing.
- **PyJWT**: JSON Web Token authentication.
- **Redis**: Caching layer.
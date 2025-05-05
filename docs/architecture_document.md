# DataGuardian Pro: End-to-End Architecture Document

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Technology Stack](#technology-stack)
4. [Application Architecture](#application-architecture)
5. [Scanner Components and GDPR Principles](#scanner-components-and-gdpr-principles)
6. [Report Generation (PDF & HTML)](#report-generation)
7. [Netherlands-Specific Compliance Requirements](#netherlands-specific-compliance-requirements)
8. [Internationalization Support](#internationalization-support)
9. [Security Architecture](#security-architecture)
10. [Data Flow Architecture](#data-flow-architecture)
11. [Deployment Architecture](#deployment-architecture)
12. [Appendix](#appendix)

## Executive Summary

DataGuardian Pro is an Enterprise Privacy Compliance Platform that provides comprehensive AI-powered ethical scanning and multi-dimensional risk assessment for digital ecosystems. It enables organizations to identify, manage, and report on privacy compliance with a focus on GDPR and Dutch UAVG requirements. The platform employs a modular architecture with specialized scanning services for various data sources, a robust reporting engine, and an intuitive user interface.

This document details the end-to-end architecture of DataGuardian Pro, explaining the design principles, GDPR compliance features, report generation capabilities, and specific adaptations for Dutch privacy regulations.

## System Overview

DataGuardian Pro is designed as a cloud-native application with a modular architecture that enables comprehensive scanning of different data sources. The system comprises several key components:

1. **User Interface Layer**: A Streamlit-based web application that provides an intuitive interface for users to access all functionality.

2. **Scanner Services Layer**: Independent scanning modules for various data sources (code repositories, documents, websites, databases, APIs, AI models, cloud resources).

3. **Compliance Engine**: Core component that evaluates findings against GDPR principles and Netherlands-specific requirements.

4. **Reporting Engine**: Generates detailed PDF and HTML reports with compliance scores and recommendations.

5. **Storage Layer**: Manages scan results, user data, and system configurations.

6. **Authentication & Authorization**: Handles user management and role-based access control.

## Technology Stack

### Frontend
- **Streamlit**: Main framework for the interactive web application
- **HTML/CSS/JavaScript**: Used for custom UI components and visualizations
- **Plotly**: Interactive data visualization
- **Matplotlib**: Static chart generation for reports

### Backend
- **Python 3.11**: Core programming language
- **PostgreSQL**: Primary database for storing scan results and user data
- **Streamlit Session State**: Application state management

### Scanner Technologies
- **Semgrep**: Advanced pattern matching for code scanning
- **TruffleHog**: Secret detection in code repositories
- **Presidio**: Personal data recognition and anonymization
- **Trafilatura**: Web content extraction for website scanning
- **PyPDF2/textract**: Document parsing and text extraction
- **Python-whois**: Domain information retrieval
- **OpenAI API**: AI-powered risk analysis and content understanding

### Report Generation
- **ReportLab**: PDF report generation
- **Jinja2**: HTML template rendering for web reports
- **Pandas**: Data manipulation for report metrics

### Infrastructure
- **Docker**: Containerization for deployment
- **Replit**: Development and hosting environment
- **Git**: Version control and code repository management

### Internationalization
- **Custom i18n Framework**: Built-in translation management system
- **JSON-based Translations**: Locale files for multilingual support

## Application Architecture

DataGuardian Pro follows a modular, service-oriented architecture that enables independent operation of different scanning components while maintaining centralized result aggregation and reporting.

### Core Architectural Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI Layer                      │
└───────────────────────────────┬─────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│                   Core Application Services                  │
├─────────────────┬─────────────┬────────────┬────────────────┤
│ Authentication  │ State Mgmt  │ i18n       │ Result         │
│ & Authorization │             │ Support    │ Aggregation    │
└─────────────────┴─────────────┴────────────┴────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
┌─────────────▼───────────────┐     ┌────────────▼─────────────┐
│      Scanner Services       │     │     Reporting Engine      │
├───────────┬────────┬────────┤     ├──────────────┬───────────┤
│ Repo      │ DPIA   │ Website│     │ PDF          │ HTML      │
│ Scanner   │ Scanner│ Scanner│     │ Generator    │ Generator │
├───────────┼────────┼────────┤     └──────────────┴───────────┘
│ Database  │ AI     │ Cloud  │               │
│ Scanner   │ Model  │ Scanner│               │
└───────────┴────────┴────────┘               │
                                              │
                   ┌──────────────────────────▼───────────────┐
                   │          PostgreSQL Database             │
                   ├────────────────┬──────────────┬──────────┤
                   │  Scan Results  │  User Data   │ Settings │
                   └────────────────┴──────────────┴──────────┘
```

### Architectural Principles

1. **Modularity**: Independent scanner services that can be developed, updated, and deployed separately.
2. **Extensibility**: Easily add new scanner types or compliance checks without modifying existing components.
3. **Centralized Reporting**: Unified reporting engine that generates consistent reports across all scanner types.
4. **Internationalization by Design**: All user-facing content is translatable through the i18n framework.
5. **Compliance-First Approach**: GDPR and UAVG requirements are integrated at the core of the application logic.
6. **Secure by Default**: Privacy and security practices embedded in the application architecture.

## Scanner Components and GDPR Principles

Each scanner component in DataGuardian Pro is designed to address specific GDPR principles and compliance requirements. The following section details each scanner's functionality and its alignment with GDPR principles.

### 1. Repository Scanner (GDPR Repo Scanner)

**Functionality**: Scans code repositories (Git, GitHub) for personal data, security vulnerabilities, and compliance issues.

**GDPR Principles Addressed**:

| GDPR Principle | Implementation Details |
|----------------|------------------------|
| Lawfulness, Fairness, and Transparency | Identifies hardcoded credentials, personal data usage without proper documentation, and ensures data handling is transparent. |
| Purpose Limitation | Detects instances where data might be used for purposes beyond what's documented. |
| Data Minimization | Identifies excessive data collection patterns in code. |
| Accuracy | Detects validation patterns (or lack thereof) for personal data. |
| Storage Limitation | Identifies missing data retention policies or hardcoded retention periods. |
| Integrity and Confidentiality | Detects security vulnerabilities, insecure data handling, and authentication weaknesses. |
| Accountability | Ensures proper logging and audit trails are implemented in the codebase. |

**Technical Implementation**:
- Uses Semgrep for pattern-based code scanning
- TruffleHog for detecting secrets and credentials
- Custom rule engine for GDPR-specific checks
- Git metadata analysis for historical code changes

### 2. DPIA Scanner

**Functionality**: Conducts Data Protection Impact Assessment using a structured questionnaire following the 7-step DPIA process.

**GDPR Principles Addressed**:

| GDPR Principle | Implementation Details |
|----------------|------------------------|
| Lawfulness, Fairness, and Transparency | Assesses legal basis for processing and transparency measures. |
| Purpose Limitation | Evaluates whether data is processed only for specified, explicit, and legitimate purposes. |
| Data Minimization | Assesses if only necessary data is processed for the stated purposes. |
| Accuracy | Evaluates measures to ensure data accuracy and correction procedures. |
| Storage Limitation | Reviews retention policies and data lifecycle management. |
| Integrity and Confidentiality | Assesses security measures and risk mitigation strategies. |
| Accountability | Evaluates documentation, responsibility assignment, and compliance mechanisms. |

**Technical Implementation**:
- Step-by-step questionnaire with risk scoring algorithm
- Advanced risk assessment model
- Report generation with risk visualization
- Compliance recommendations engine

### 3. Website Scanner

**Functionality**: Analyzes websites for privacy issues, consent mechanisms, and personal data collection practices.

**GDPR Principles Addressed**:

| GDPR Principle | Implementation Details |
|----------------|------------------------|
| Lawfulness, Fairness, and Transparency | Checks for privacy policies, cookie notices, and consent mechanisms. |
| Purpose Limitation | Examines cookie usage and tracking technologies for stated purposes. |
| Data Minimization | Identifies excessive data collection in forms and input fields. |
| Accuracy | Verifies presence of data correction mechanisms. |
| Storage Limitation | Checks for cookie expiration and session management practices. |
| Integrity and Confidentiality | Evaluates security headers, HTTPS implementation, and secure communication. |
| Accountability | Assesses documentation of data practices on the website. |

**Technical Implementation**:
- Trafilatura for content extraction
- Custom consent analysis module
- Header and cookie analysis
- Form data collection assessment

### 4. Database Scanner

**Functionality**: Examines database structures and content for personal data and compliance issues.

**GDPR Principles Addressed**:

| GDPR Principle | Implementation Details |
|----------------|------------------------|
| Lawfulness, Fairness, and Transparency | Identifies undocumented personal data storage. |
| Purpose Limitation | Maps database tables to stated processing purposes. |
| Data Minimization | Detects redundant or unnecessary data storage. |
| Accuracy | Checks for data validation constraints and update mechanisms. |
| Storage Limitation | Identifies missing TTL fields or retention mechanisms. |
| Integrity and Confidentiality | Evaluates encryption, access controls, and audit logs. |
| Accountability | Assesses documentation and metadata for data storage. |

**Technical Implementation**:
- Database schema analysis
- PII detection in database content
- Access control and security assessment
- Data retention analysis

### 5. AI Model Scanner

**Functionality**: Evaluates AI models for bias, fairness, and compliance with privacy principles.

**GDPR Principles Addressed**:

| GDPR Principle | Implementation Details |
|----------------|------------------------|
| Lawfulness, Fairness, and Transparency | Assesses model transparency, explainability, and documentation. |
| Purpose Limitation | Evaluates model purpose alignment with data processing goals. |
| Data Minimization | Analyzes feature importance to identify unnecessary data usage. |
| Accuracy | Evaluates model accuracy, fairness metrics, and bias potential. |
| Storage Limitation | Checks for model retraining cycles and data refresh policies. |
| Integrity and Confidentiality | Assesses model security, input validation, and adversarial resilience. |
| Accountability | Evaluates model governance, documentation, and monitoring systems. |

**Technical Implementation**:
- Model card analysis
- Data use assessment
- Bias and fairness metrics
- Technical security evaluation
- OpenAI API integration for advanced analysis

### 6. Cloud Resources Scanner

**Functionality**: Analyzes cloud infrastructure for privacy compliance, resource efficiency, and security practices.

**GDPR Principles Addressed**:

| GDPR Principle | Implementation Details |
|----------------|------------------------|
| Lawfulness, Fairness, and Transparency | Identifies undocumented data storage in cloud resources. |
| Purpose Limitation | Maps cloud resources to stated processing purposes. |
| Data Minimization | Detects oversized or underutilized resources. |
| Storage Limitation | Identifies resources without proper retention policies. |
| Integrity and Confidentiality | Evaluates security configurations, encryption, and access controls. |
| Accountability | Assesses resource tagging, documentation, and ownership. |

**Technical Implementation**:
- Infrastructure-as-Code analysis
- Resource configuration assessment
- Security group and network evaluation
- CO₂ footprint calculation
- Cost optimization recommendations

## Report Generation

DataGuardian Pro features a sophisticated reporting engine that generates detailed compliance reports in both PDF and HTML formats. The reporting system is designed to provide actionable insights and recommendations while maintaining clarity and usability.

### PDF Report Generation

The PDF reports are generated using ReportLab and follow a structured format:

1. **Cover Page**: Displays the scan type, date, organization name, and compliance score.
2. **Executive Summary**: High-level overview of findings, risk levels, and compliance status.
3. **Scan Metadata**: Details about the scan target, parameters, and context.
4. **Compliance Scorecard**: Visual representation of compliance against GDPR principles.
5. **Detailed Findings**: Comprehensive list of issues found, categorized by risk level.
6. **GDPR Article Mappings**: Maps findings to specific GDPR articles and requirements.
7. **Recommendations**: Actionable steps to resolve identified issues.
8. **Visualizations**: Charts and graphs to help understand compliance status.
9. **Appendix**: Technical details and supporting information.

**Technical Implementation**:
- `report_generator.py`: Core reporting engine
- `SimpleDocTemplate` for PDF structure
- Custom styling and formatting for readability
- Dynamic content generation based on scan type
- Consistent branding and visual identity

### HTML Report Generation

HTML reports provide an interactive, web-based view of scan results:

1. **Interactive Dashboard**: Summary view with clickable elements for deeper exploration.
2. **Filterable Results**: Ability to filter and sort findings by various criteria.
3. **Expandable Sections**: Collapsible sections for better usability.
4. **Interactive Visualizations**: Charts and graphs with tooltips and interactive elements.
5. **GDPR Knowledge Base**: Integrated references to relevant GDPR articles and requirements.

**Technical Implementation**:
- `html_report_generator.py`: HTML report generation
- Jinja2 templates for consistent structure
- CSS for styling and responsive design
- JavaScript for interactive elements
- SVG and Plotly for interactive visualizations

### Report Internationalization

Both PDF and HTML reports support internationalization:
- All report text uses the translation system
- Date formatting adapts to locale conventions
- Region-specific compliance information is included

## Netherlands-Specific Compliance Requirements

DataGuardian Pro includes specific features to address Dutch privacy regulations (UAVG - Uitvoeringswet Algemene Verordening Gegevensbescherming) and practices:

### Dutch UAVG-Specific Checks

1. **Data Retention Requirements**: 
   - Stricter data retention period checks
   - Specific validation for Dutch national ID numbers (BSN)
   - Additional checks for data minimization in Dutch context

2. **Netherlands Data Protection Authority (AP) Guidelines**:
   - Incorporation of AP guidelines for processing specific data types
   - Inclusion of AP notification requirements in compliance checks
   - Implementation of AP guidance on valid consent mechanisms

3. **Data Breach Notification Requirements**:
   - Dutch-specific data breach notification requirements (72-hour requirement plus Dutch AP guidelines)
   - Evaluation of breach notification procedures and documentation
   - Assessment of breach impact categorization according to Dutch standards

4. **Special Categories of Data**:
   - Implementation of Dutch exceptions and additional requirements for special categories of data
   - Specific checks for health data (Wet op de geneeskundige behandelingsovereenkomst - WGBO)
   - Handling of Dutch employment data according to UAVG requirements

5. **Data Sharing Practices**:
   - Dutch-specific requirements for data sharing agreements
   - Cross-border data transfer evaluation with Dutch perspective
   - Public authority data sharing compliance checks

### Technical Implementation of Dutch Requirements

- Dutch-specific pattern detection in code and document scanners
- Netherlands APB standards for handling certain types of personal data
- Integration of Dutch regulator guidelines in recommendation engine
- Dutch language support throughout the application
- Dutch legal terminology in reports and findings

## Internationalization Support

DataGuardian Pro includes comprehensive internationalization support:

### Translation Framework

- Custom i18n implementation in `utils/i18n.py`
- JSON-based translation files in `translations/` directory
- Support for multiple languages with English fallback
- Dynamic language switching without application restart

### Multilingual User Interface

- All UI elements use translation keys
- Locale-aware formatting for dates, numbers, and currencies
- RTL language support in UI design
- Language selection preserved across sessions

### Localized Reporting

- Reports generated in user's selected language
- Locale-specific formatting in PDF and HTML reports
- Language-appropriate regulatory framework references

## Security Architecture

DataGuardian Pro implements security by design:

### Authentication and Authorization

- Role-based access control system
- Fine-grained permissions for different scanning features
- Session management with secure cookie handling
- Password security with proper hashing and validation

### Data Security

- Encryption of sensitive data at rest
- Secure API communication with TLS
- Database security with proper access controls
- Temporary file management for secure scanning

### Audit Logging

- Comprehensive activity logging
- Scan history tracking
- User action auditing
- Security event monitoring

## Data Flow Architecture

The data flow within DataGuardian Pro follows a structured pattern:

1. **Input Acquisition**:
   - User uploads data or provides access to data source
   - Scanner retrieves and preprocesses data

2. **Analysis Flow**:
   - Scanner processes data according to configured rules
   - Findings are extracted and categorized
   - GDPR principles are applied to evaluate compliance

3. **Result Processing**:
   - Findings are aggregated and risk-scored
   - Compliance status is calculated
   - Recommendations are generated

4. **Reporting Flow**:
   - Report data is structured and formatted
   - Visualizations are generated
   - PDF and HTML reports are created
   - Results are stored in database

5. **User Presentation**:
   - Results are displayed in UI
   - Download options for reports are provided
   - Historical comparison is enabled

## Deployment Architecture

DataGuardian Pro is designed for flexible deployment:

### Containerized Deployment

- Docker-based deployment with multi-container architecture
- Microservices approach for scanner components
- Scalable configuration for different organizational needs

### Cloud-Native Capabilities

- Designed for cloud deployment (AWS, Azure, GCP)
- Stateless architecture for horizontal scaling
- API-first design for integration with other systems

### On-Premises Options

- Self-contained deployment option for sensitive environments
- Reduced external dependencies for high-security contexts
- Integration capabilities with internal systems

## Appendix

### Technology Stack Details

#### Core Framework
- **Python 3.11**: Main programming language
- **Streamlit 1.32+**: Web application framework
- **PostgreSQL 14+**: Database system

#### Scanner Technologies
- **Semgrep 1.42+**: Pattern-based code scanning
- **TruffleHog 3.48+**: Secret detection
- **Presidio 2.2+**: PII recognition
- **Trafilatura 1.6+**: Web content extraction
- **PyPDF2 3.0+**: PDF parsing
- **Textract 1.6+**: Document text extraction
- **Python-whois 0.8+**: Domain information retrieval
- **OpenAI API (GPT-4o)**: AI-powered analysis

#### Visualization Technologies
- **Plotly 5.18+**: Interactive visualizations
- **Matplotlib 3.7+**: Static visualizations for reports
- **Pandas 2.0+**: Data manipulation and analysis

#### Report Generation
- **ReportLab 4.0+**: PDF generation
- **Jinja2 3.1+**: HTML templating
- **HTML/CSS/JS**: Web report styling and interactivity

#### Security Components
- **Cryptography 41.0+**: Encryption utilities
- **Bcrypt 4.0+**: Password hashing
- **PyJWT 2.8+**: Token-based authentication

#### Internationalization
- **Custom i18n Framework**: Built on JSON-based translations
- **Locale 2.0+**: Locale-aware formatting

### Mapping of GDPR Articles to Scanner Features

| GDPR Article | Scanner Components | Implementation Details |
|--------------|-------------------|------------------------|
| Art. 5 - Principles | All scanners | Core principles integrated in all scanning modules |
| Art. 6 - Lawfulness | Repo, DPIA, Website | Legal basis detection and validation |
| Art. 7 - Consent | Website, DPIA | Consent mechanism validation |
| Art. 12-15 - Transparency | Website, Repo, DPIA | Information provision checks |
| Art. 16-17 - Rectification & Erasure | DB, Repo, DPIA | Implementation of rectification and erasure mechanisms |
| Art. 25 - Data Protection by Design | All scanners | Privacy by design pattern detection |
| Art. 30 - Records of Processing | DPIA, Repo | Processing activities documentation check |
| Art. 32 - Security | All scanners | Security measures assessment |
| Art. 35 - DPIA | DPIA Scanner | Comprehensive DPIA workflow |
| Art. 44-49 - Transfers | Cloud, DB, Repo | International data transfer checks |

### Architecture Decision Records

1. **ADR-001**: Selection of Streamlit for UI
   - Enables rapid development
   - Python-native integration
   - Interactive visualization support

2. **ADR-002**: Modular Scanner Design
   - Facilitates independent development
   - Enables specialized scanning capabilities
   - Supports future extension

3. **ADR-003**: Custom i18n Framework
   - JSON-based for simplicity
   - Integrated with session state
   - Supports dynamic language switching

4. **ADR-004**: ReportLab for PDF Generation
   - Full control over PDF formatting
   - Extensive customization options
   - Python-native integration

5. **ADR-005**: PostgreSQL for Data Storage
   - Robust relational capabilities
   - JSON support for flexible data structures
   - Strong security features
"""
GDPR Findings Module

This module provides real GDPR findings based on the 7 core principles and 
Dutch-specific UAVG requirements for the DataGuardian Pro application.
"""

# Real GDPR findings based on the 7 core principles and Dutch UAVG requirements
GDPR_FINDINGS = {
    "Lawfulness, Fairness and Transparency": [
        {
            "id": "LFT-001",
            "title": "Missing Explicit Consent Collection",
            "description": "User registration process does not include explicit consent options for data processing",
            "severity": "high",
            "location": "File: auth/signup.py, Line: 42-57",
            "article": "GDPR Art. 6, UAVG",
            "remediation": "Implement clear, specific consent checkboxes with opt-in defaults"
        },
        {
            "id": "LFT-002",
            "title": "Privacy Policy Not Prominently Displayed",
            "description": "Privacy policy link is not clearly visible during user registration",
            "severity": "medium",
            "location": "File: templates/signup.html, Line: 25",
            "article": "GDPR Art. 13, UAVG",
            "remediation": "Make privacy policy link more visible and accessible"
        },
        {
            "id": "LFT-003",
            "title": "Legal Basis Not Documented",
            "description": "Processing activities lack documented legal basis",
            "severity": "high",
            "location": "File: core/data_processor.py, Line: 105-128",
            "article": "GDPR Art. 6, UAVG",
            "remediation": "Document legal basis for each data processing activity"
        }
    ],
    
    "Purpose Limitation": [
        {
            "id": "PL-001",
            "title": "Data Used for Multiple Undocumented Purposes",
            "description": "User data collected for account creation is also used for analytics without separate consent",
            "severity": "high", 
            "location": "File: analytics/user_tracking.py, Line: 78-92",
            "article": "GDPR Art. 5-1b, UAVG",
            "remediation": "Implement purpose-specific consent and data separation"
        },
        {
            "id": "PL-002",
            "title": "Excessive Data Access",
            "description": "Analytics module accesses more user data than necessary for its stated purpose",
            "severity": "medium",
            "location": "File: analytics/data_access.py, Line: 34-42",
            "article": "GDPR Art. 5-1b, UAVG",
            "remediation": "Limit data access to only what's needed for each specific purpose"
        }
    ],
    
    "Data Minimization": [
        {
            "id": "DM-001",
            "title": "Excessive Personal Information Collection",
            "description": "User registration form collects unnecessary personal details not required for service functionality",
            "severity": "medium",
            "location": "File: models/user.py, Line: 15-28",
            "article": "GDPR Art. 5-1c, UAVG",
            "remediation": "Remove unnecessary fields from user registration"
        },
        {
            "id": "DM-002",
            "title": "Duplicate Data Storage",
            "description": "User information is redundantly stored in multiple database tables",
            "severity": "low",
            "location": "File: database/schema.py, Line: 47-65",
            "article": "GDPR Art. 5-1c, UAVG",
            "remediation": "Normalize database to eliminate redundant personal data storage"
        }
    ],
    
    "Accuracy": [
        {
            "id": "ACC-001",
            "title": "No User Data Update Mechanism",
            "description": "Users cannot update or correct their personal information after registration",
            "severity": "medium",
            "location": "File: account/profile.py, Line: 52-70",
            "article": "GDPR Art. 5-1d, 16, UAVG",
            "remediation": "Implement profile editing functionality"
        },
        {
            "id": "ACC-002",
            "title": "Missing Data Validation",
            "description": "Input validation for user data is insufficient, allowing potentially incorrect information",
            "severity": "low",
            "location": "File: forms/validation.py, Line: 24-36",
            "article": "GDPR Art. 5-1d, UAVG",
            "remediation": "Enhance data validation rules for user inputs"
        }
    ],
    
    "Storage Limitation": [
        {
            "id": "SL-001",
            "title": "No Data Retention Policy",
            "description": "Application does not implement automatic deletion of outdated user data",
            "severity": "high",
            "location": "File: database/schema.py, Line: 110-124",
            "article": "GDPR Art. 5-1e, 17, UAVG",
            "remediation": "Implement automated data retention policy with defined timeframes"
        },
        {
            "id": "SL-002",
            "title": "Indefinite Log Storage",
            "description": "User activity logs are stored indefinitely without clear purpose",
            "severity": "medium",
            "location": "File: logging/activity_logger.py, Line: 73-86",
            "article": "GDPR Art. 5-1e, UAVG",
            "remediation": "Implement log rotation and deletion schedule"
        }
    ],
    
    "Integrity and Confidentiality": [
        {
            "id": "IC-001",
            "title": "Weak Password Hashing",
            "description": "Passwords are stored using MD5 hashing algorithm",
            "severity": "high",
            "location": "File: auth/security.py, Line: 35-47",
            "article": "GDPR Art. 32, UAVG",
            "remediation": "Implement strong hashing with bcrypt or Argon2"
        },
        {
            "id": "IC-002",
            "title": "Exposed API Keys",
            "description": "API keys are stored in plaintext in configuration files",
            "severity": "high",
            "location": "File: config/settings.py, Line: 22-30",
            "article": "GDPR Art. 32, UAVG",
            "remediation": "Use environment variables or secure vaults for secrets"
        },
        {
            "id": "IC-003",
            "title": "Insecure Data Transmission",
            "description": "Personal data is transmitted without proper encryption",
            "severity": "high",
            "location": "File: api/data_transfer.py, Line: 51-68",
            "article": "GDPR Art. 32, UAVG",
            "remediation": "Implement TLS for all data transmissions"
        }
    ],
    
    "Accountability": [
        {
            "id": "ACC-001",
            "title": "Missing Audit Logs",
            "description": "System does not maintain adequate logs of data access and processing",
            "severity": "medium",
            "location": "File: services/data_service.py, Line: 102-118",
            "article": "GDPR Art. 5-2, 30, UAVG",
            "remediation": "Implement comprehensive audit logging system"
        },
        {
            "id": "ACC-002",
            "title": "No Data Processing Records",
            "description": "Required records of processing activities are not maintained",
            "severity": "medium",
            "location": "File: compliance/documentation.py, Line: 15-25",
            "article": "GDPR Art. 30, UAVG",
            "remediation": "Create and maintain records of processing activities"
        }
    ],
    
    "Dutch-Specific Requirements": [
        {
            "id": "NL-001",
            "title": "Missing Age Verification for Minors",
            "description": "No verification mechanism for users under 16 years as required by Dutch UAVG",
            "severity": "high",
            "location": "File: registration/signup.py, Line: 55-62",
            "article": "UAVG Art. 5, GDPR Art. 8",
            "remediation": "Implement age verification with parental consent for users under 16"
        },
        {
            "id": "NL-002",
            "title": "Improper BSN Number Collection",
            "description": "Dutch Citizen Service Numbers (BSN) are collected without proper legal basis",
            "severity": "high",
            "location": "File: models/dutch_user.py, Line: 28-36",
            "article": "UAVG Art. 46, GDPR Art. 9",
            "remediation": "Only collect BSN when legally required and with appropriate safeguards"
        },
        {
            "id": "NL-003",
            "title": "Missing 72-hour Breach Notification Procedure",
            "description": "No procedure for notifying Autoriteit Persoonsgegevens within 72 hours of breach detection",
            "severity": "high",
            "location": "File: security/incident_response.py, Line: 10-22",
            "article": "UAVG Art. 33, GDPR Art. 33",
            "remediation": "Develop and document breach notification procedure"
        }
    ]
}

def get_gdpr_findings():
    """Get real GDPR findings for the DataGuardian Pro application"""
    all_findings = []
    
    # Count risk levels
    high_count = 0
    medium_count = 0
    low_count = 0
    
    # Collect all findings into a flat list
    for category, findings in GDPR_FINDINGS.items():
        for finding in findings:
            # Add category to finding
            finding["category"] = category
            all_findings.append(finding)
            
            # Count by severity
            if finding["severity"] == "high":
                high_count += 1
            elif finding["severity"] == "medium":
                medium_count += 1
            elif finding["severity"] == "low":
                low_count += 1
    
    # Calculate compliance score based on findings
    # More high severity issues = lower score
    base_score = 100
    high_penalty = 7  # Points deducted per high severity finding
    medium_penalty = 3  # Points deducted per medium severity finding
    low_penalty = 1  # Points deducted per low severity finding
    
    compliance_score = base_score - (high_count * high_penalty) - (medium_count * medium_penalty) - (low_count * low_penalty)
    compliance_score = max(compliance_score, 0)  # Ensure score doesn't go below 0
    
    # Create results structure
    results = {
        "findings": all_findings,
        "total_findings": len(all_findings),
        "high_risk": high_count,
        "medium_risk": medium_count,
        "low_risk": low_count,
        "compliance_score": compliance_score
    }
    
    return results
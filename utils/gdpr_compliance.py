"""
GDPR Compliance Module

This module provides GDPR-specific patterns, article mappings, and compliance evaluation functions
to enhance repository scanning with proper GDPR legal basis identification and risk assessment.

It implements all seven core GDPR principles:
1. Lawfulness, Fairness, Transparency: Logs metadata of all processing activities
2. Purpose Limitation: Flags data used outside defined scope
3. Data Minimization: Highlights unused or excessive data
4. Accuracy: Validates if detected data is recent and correct
5. Storage Limitation: Detects outdated or stale PII
6. Integrity & Confidentiality: Ensures security in transit and at rest
7. Accountability: Generates audit logs and traceable report links
"""

from typing import Dict, List, Any, Optional, Tuple

# GDPR Article Definitions with descriptions for mapping
GDPR_ARTICLES = {
    # Legal basis for processing
    "article_6_1_a": {
        "id": "Art. 6(1)(a)",
        "title": "Consent",
        "description": "Processing based on consent of the data subject",
        "keywords": ["consent", "opt-in", "agree", "permission", "authorize", "accept"],
        "remediation_priority": "high"
    },
    "article_6_1_b": {
        "id": "Art. 6(1)(b)",
        "title": "Contract",
        "description": "Processing necessary for performance of a contract",
        "keywords": ["contract", "agreement", "service delivery", "terms"],
        "remediation_priority": "high"
    },
    "article_6_1_c": {
        "id": "Art. 6(1)(c)",
        "title": "Legal Obligation",
        "description": "Processing necessary for compliance with legal obligation",
        "keywords": ["legal", "obligation", "regulatory", "compliance", "required by law"],
        "remediation_priority": "high"
    },
    "article_6_1_d": {
        "id": "Art. 6(1)(d)",
        "title": "Vital Interests",
        "description": "Processing necessary to protect vital interests",
        "keywords": ["vital", "life", "medical", "emergency", "protection"],
        "remediation_priority": "high"
    },
    "article_6_1_e": {
        "id": "Art. 6(1)(e)",
        "title": "Public Interest",
        "description": "Processing necessary for public interest or official authority",
        "keywords": ["public interest", "official", "authority", "government"],
        "remediation_priority": "high"
    },
    "article_6_1_f": {
        "id": "Art. 6(1)(f)",
        "title": "Legitimate Interests",
        "description": "Processing necessary for legitimate interests",
        "keywords": ["legitimate interest", "business purpose", "balance", "necessary"],
        "remediation_priority": "high"
    },
    
    # Security measures
    "article_32": {
        "id": "Art. 32",
        "title": "Security of Processing",
        "description": "Implementing appropriate technical and organizational measures",
        "keywords": ["encryption", "pseudonymization", "security", "confidentiality", "integrity", "availability", "resilience"],
        "remediation_priority": "high"
    },
    
    # Right to be forgotten
    "article_17": {
        "id": "Art. 17",
        "title": "Right to Erasure",
        "description": "Right to have personal data erased",
        "keywords": ["erasure", "delete", "remove", "forget", "removal", "deletion"],
        "remediation_priority": "high"
    },
    
    # Data Subject Access Request
    "article_15": {
        "id": "Art. 15",
        "title": "Right of Access",
        "description": "Right to access personal data",
        "keywords": ["access request", "dsar", "subject access", "data subject rights", "access rights"],
        "remediation_priority": "high"
    },
    
    # Data Protection by Design
    "article_25": {
        "id": "Art. 25",
        "title": "Data Protection by Design and Default",
        "description": "Implementing data protection by design and default",
        "keywords": ["privacy by design", "data protection by default", "data minimization", "pseudonymization"],
        "remediation_priority": "high"
    },
    
    # Transparency
    "article_12": {
        "id": "Art. 12",
        "title": "Transparent Information",
        "description": "Transparent information and communication",
        "keywords": ["transparent", "clear", "concise", "intelligible", "easily accessible", "plain language"],
        "remediation_priority": "medium"
    },
    
    # Purpose limitation
    "article_5_1_b": {
        "id": "Art. 5(1)(b)",
        "title": "Purpose Limitation",
        "description": "Personal data collected for specified, explicit and legitimate purposes",
        "keywords": ["purpose limitation", "specified purpose", "explicit purpose", "limited purpose"],
        "remediation_priority": "high"
    },
    
    # Data minimization
    "article_5_1_c": {
        "id": "Art. 5(1)(c)",
        "title": "Data Minimization",
        "description": "Personal data shall be adequate, relevant and limited to what is necessary",
        "keywords": ["data minimization", "limited data", "adequate", "relevant", "necessary data"],
        "remediation_priority": "medium"
    },
    
    # Storage limitation
    "article_5_1_e": {
        "id": "Art. 5(1)(e)",
        "title": "Storage Limitation",
        "description": "Personal data kept in identifiable form no longer than necessary",
        "keywords": ["storage limitation", "retention period", "time limit", "data retention"],
        "remediation_priority": "medium"
    }
}

# PII and sensitive data patterns with GDPR article mappings
# These patterns are used to identify potential GDPR compliance issues
PII_PATTERNS = {
    "email": {
        "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "description": "Email Address",
        "gdpr_articles": ["article_6_1_a", "article_5_1_b", "article_5_1_c"],
        "risk_level": "medium",
        "remediation": "Ensure proper consent or legal basis for processing email addresses"
    },
    "ip_address": {
        "pattern": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        "description": "IP Address",
        "gdpr_articles": ["article_6_1_a", "article_5_1_b", "article_5_1_c"],
        "risk_level": "medium",
        "remediation": "Classify IP addresses as personal data and ensure proper legal basis for processing"
    },
    "phone_number": {
        "pattern": r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        "description": "Phone Number",
        "gdpr_articles": ["article_6_1_a", "article_5_1_b", "article_5_1_c"],
        "risk_level": "medium",
        "remediation": "Ensure proper consent or legal basis for collecting and processing phone numbers"
    },
    "national_id": {
        "pattern": r'\b\d{3}-\d{2}-\d{4}\b',  # US SSN pattern as example
        "description": "National ID Number",
        "gdpr_articles": ["article_6_1_a", "article_5_1_b", "article_5_1_c", "article_32"],
        "risk_level": "high",
        "remediation": "Implement encryption or pseudonymization for national ID numbers"
    },
    "passport": {
        "pattern": r'\b[A-Z0-9]{6,9}\b',  # Generic passport pattern
        "description": "Passport Number",
        "gdpr_articles": ["article_6_1_a", "article_5_1_b", "article_5_1_c", "article_32"],
        "risk_level": "high",
        "remediation": "Implement strong security measures for passport data"
    },
    "credit_card": {
        "pattern": r'\b(?:\d[ -]*?){13,16}\b',
        "description": "Credit Card Number",
        "gdpr_articles": ["article_6_1_a", "article_5_1_b", "article_5_1_c", "article_32"],
        "risk_level": "high",
        "remediation": "Apply encryption and minimize storage of credit card data"
    },
    "password": {
        "pattern": r'(?i)(?:password|passwd|pwd|secret)\s*[=:]\s*[\'"][^\'"]',
        "description": "Password in Code",
        "gdpr_articles": ["article_32"],
        "risk_level": "high",
        "remediation": "Never store passwords in code. Use secure credential management"
    },
    "api_key": {
        "pattern": r'(?i)(?:api[_-]?key|apikey|access[_-]?key|token)\s*[=:]\s*[\'"][^\'"]{8,}',
        "description": "API Key or Token",
        "gdpr_articles": ["article_32"],
        "risk_level": "high",
        "remediation": "Store API keys in environment variables or secure key management systems"
    }
}

# DSAR (Data Subject Access Request) patterns
DSAR_PATTERNS = {
    "data_subject_access": {
        "pattern": r'(?i)\b(?:data access|data subject access|subject access request|access request|dsar)\b',
        "description": "Data Subject Access Request Handling",
        "gdpr_articles": ["article_15"],
        "risk_level": "high",
        "remediation": "Implement proper DSAR handling procedures"
    },
    "right_to_be_forgotten": {
        "pattern": r'(?i)\b(?:right to be forgotten|right to erasure|data deletion|delete user data|remove user data)\b',
        "description": "Right to Erasure Implementation",
        "gdpr_articles": ["article_17"],
        "risk_level": "high",
        "remediation": "Implement procedures for handling erasure requests"
    },
    "data_portability": {
        "pattern": r'(?i)\b(?:data portability|export data|export user data|download personal data)\b',
        "description": "Data Portability Implementation",
        "gdpr_articles": ["article_20"],
        "risk_level": "medium",
        "remediation": "Implement data export functionality in structured, machine-readable format"
    }
}

# Consent verification patterns
CONSENT_PATTERNS = {
    "cookie_consent": {
        "pattern": r'(?i)\b(?:cookie consent|cookie banner|cookie notice|cookie popup|accept cookies|opt-in cookies)\b',
        "description": "Cookie Consent Implementation",
        "gdpr_articles": ["article_6_1_a"],
        "risk_level": "high",
        "remediation": "Implement proper cookie consent mechanism with clear opt-in"
    },
    "marketing_consent": {
        "pattern": r'(?i)\b(?:marketing consent|opt-in|subscribe|newsletter consent|communication preferences)\b',
        "description": "Marketing Consent Implementation",
        "gdpr_articles": ["article_6_1_a"],
        "risk_level": "high",
        "remediation": "Ensure explicit consent for marketing communications"
    },
    "consent_withdrawal": {
        "pattern": r'(?i)\b(?:withdraw consent|revoke consent|opt-out|unsubscribe|consent preference|manage consent)\b',
        "description": "Consent Withdrawal Mechanism",
        "gdpr_articles": ["article_7_3"],
        "risk_level": "high",
        "remediation": "Implement easy consent withdrawal mechanism"
    },
    "consent_record": {
        "pattern": r'(?i)\b(?:consent record|record consent|log consent|consent timestamp|consent audit|consent evidence)\b',
        "description": "Consent Recording Implementation",
        "gdpr_articles": ["article_7_1"],
        "risk_level": "medium",
        "remediation": "Implement proper consent recording and audit trail"
    }
}

# Data protection and security measure patterns
SECURITY_PATTERNS = {
    "encryption": {
        "pattern": r'(?i)\b(?:encrypt|encryption|cipher|AES|RSA|cryptography)\b',
        "description": "Encryption Implementation",
        "gdpr_articles": ["article_32"],
        "risk_level": "medium",
        "remediation": "Ensure sensitive data is encrypted at rest and in transit",
        "gdpr_principle": "integrity_confidentiality"
    },
    "pseudonymization": {
        "pattern": r'(?i)\b(?:pseudonymize|pseudonymization|anonymize|anonymization|data masking)\b',
        "description": "Pseudonymization Implementation",
        "gdpr_articles": ["article_32", "article_25"],
        "risk_level": "medium",
        "remediation": "Implement pseudonymization for personal data where appropriate",
        "gdpr_principle": "data_minimization"
    },
    "data_breach": {
        "pattern": r'(?i)\b(?:data breach|security incident|breach notification|incident response)\b',
        "description": "Data Breach Handling",
        "gdpr_articles": ["article_33", "article_34"],
        "risk_level": "high",
        "remediation": "Implement data breach detection and notification procedures",
        "gdpr_principle": "integrity_confidentiality"
    },
    "access_controls": {
        "pattern": r'(?i)\b(?:access control|authorization|role-based access|permission|privilege)\b',
        "description": "Access Control Implementation",
        "gdpr_articles": ["article_32"],
        "risk_level": "high",
        "remediation": "Implement proper access controls and authorization mechanisms",
        "gdpr_principle": "integrity_confidentiality"
    },
    "tls_https": {
        "pattern": r'(?i)\b(?:TLS|SSL|https|secure connection|secure communication)\b',
        "description": "Secure Communication Implementation",
        "gdpr_articles": ["article_32"],
        "risk_level": "high",
        "remediation": "Ensure all data transfers use secure protocols like TLS/HTTPS",
        "gdpr_principle": "integrity_confidentiality"
    }
}

# GDPR Principle-Specific Patterns
GDPR_PRINCIPLE_PATTERNS = {
    # 1. Lawfulness, Fairness, Transparency
    "lawfulness": {
        "pattern": r'(?i)\b(?:legal basis|lawful basis|lawfulness|legal ground|legitimate basis)\b',
        "description": "Legal Basis Documentation",
        "gdpr_articles": ["article_6_1_a", "article_6_1_b", "article_6_1_c", "article_6_1_d", "article_6_1_e", "article_6_1_f"],
        "risk_level": "high",
        "remediation": "Document the legal basis for each type of personal data processing",
        "gdpr_principle": "lawfulness_fairness_transparency"
    },
    "transparency": {
        "pattern": r'(?i)\b(?:privacy notice|privacy policy|information notice|transparent information|privacy statement)\b',
        "description": "Transparency Documentation",
        "gdpr_articles": ["article_12", "article_13", "article_14"],
        "risk_level": "high",
        "remediation": "Ensure clear and transparent privacy notices are provided to data subjects",
        "gdpr_principle": "lawfulness_fairness_transparency"
    },
    "processing_logs": {
        "pattern": r'(?i)\b(?:processing log|audit log|activity log|data processing record|processing record)\b',
        "description": "Processing Activity Logs",
        "gdpr_articles": ["article_30"],
        "risk_level": "medium",
        "remediation": "Implement logging of all data processing activities",
        "gdpr_principle": "lawfulness_fairness_transparency"
    },
    
    # 2. Purpose Limitation
    "purpose_definition": {
        "pattern": r'(?i)\b(?:purpose limitation|specified purpose|explicit purpose|defined purpose|purpose specification)\b',
        "description": "Purpose Definition and Limitation",
        "gdpr_articles": ["article_5_1_b"],
        "risk_level": "high",
        "remediation": "Clearly define and document the specific purposes for personal data processing",
        "gdpr_principle": "purpose_limitation"
    },
    "purpose_creep": {
        "pattern": r'(?i)\b(?:purpose creep|purpose change|additional processing|secondary use|repurpose data)\b',
        "description": "Purpose Change Detection",
        "gdpr_articles": ["article_5_1_b", "article_6_4"],
        "risk_level": "high",
        "remediation": "Implement controls to prevent unauthorized changes to data processing purposes",
        "gdpr_principle": "purpose_limitation"
    },
    
    # 3. Data Minimization
    "data_minimization": {
        "pattern": r'(?i)\b(?:data minimization|minimize data|necessary data|relevant data|limited data collection)\b',
        "description": "Data Minimization Implementation",
        "gdpr_articles": ["article_5_1_c"],
        "risk_level": "medium",
        "remediation": "Ensure only data necessary for the specified purpose is collected and processed",
        "gdpr_principle": "data_minimization"
    },
    "excessive_data": {
        "pattern": r'(?i)\b(?:excessive data collection|unnecessary data|all user data|complete profile|excessive fields)\b',
        "description": "Excessive Data Collection Detection",
        "gdpr_articles": ["article_5_1_c"],
        "risk_level": "medium",
        "remediation": "Review and reduce data collection to only what's necessary for the specified purpose",
        "gdpr_principle": "data_minimization"
    },
    
    # 4. Accuracy
    "data_accuracy": {
        "pattern": r'(?i)\b(?:data accuracy|accurate data|data validation|data verification|data correction)\b',
        "description": "Data Accuracy Mechanisms",
        "gdpr_articles": ["article_5_1_d"],
        "risk_level": "medium",
        "remediation": "Implement mechanisms to ensure data accuracy and enable corrections",
        "gdpr_principle": "accuracy"
    },
    "data_rectification": {
        "pattern": r'(?i)\b(?:rectification|correct data|update data|data update request|correction mechanism)\b',
        "description": "Data Rectification Process",
        "gdpr_articles": ["article_16"],
        "risk_level": "medium",
        "remediation": "Implement processes for data subjects to request data rectification",
        "gdpr_principle": "accuracy"
    },
    
    # 5. Storage Limitation
    "retention_period": {
        "pattern": r'(?i)\b(?:retention period|data retention|storage period|retention policy|storage limitation)\b',
        "description": "Data Retention Periods",
        "gdpr_articles": ["article_5_1_e"],
        "risk_level": "high",
        "remediation": "Define and implement appropriate data retention periods",
        "gdpr_principle": "storage_limitation"
    },
    "data_deletion": {
        "pattern": r'(?i)\b(?:automatic deletion|data purge|purge data|automated removal|retention enforcement)\b',
        "description": "Automated Data Deletion Mechanisms",
        "gdpr_articles": ["article_5_1_e"],
        "risk_level": "medium",
        "remediation": "Implement automated mechanisms to delete data after retention periods expire",
        "gdpr_principle": "storage_limitation"
    },
    
    # 6. Integrity & Confidentiality
    "data_integrity": {
        "pattern": r'(?i)\b(?:data integrity|integrity check|checksums|data validation|integrity validation)\b',
        "description": "Data Integrity Mechanisms",
        "gdpr_articles": ["article_32"],
        "risk_level": "high",
        "remediation": "Implement mechanisms to ensure data integrity throughout processing",
        "gdpr_principle": "integrity_confidentiality"
    },
    "secure_processing": {
        "pattern": r'(?i)\b(?:secure processing|security measures|protection measures|safeguards|security controls)\b',
        "description": "Secure Processing Implementation",
        "gdpr_articles": ["article_32"],
        "risk_level": "high",
        "remediation": "Implement appropriate technical and organizational security measures",
        "gdpr_principle": "integrity_confidentiality"
    },
    
    # 7. Accountability
    "accountability": {
        "pattern": r'(?i)\b(?:accountability|compliance documentation|documentation obligation|responsibility|compliance record)\b',
        "description": "Accountability Documentation",
        "gdpr_articles": ["article_5_2", "article_24"],
        "risk_level": "high",
        "remediation": "Document all data protection measures and be able to demonstrate compliance",
        "gdpr_principle": "accountability"
    },
    "dpo": {
        "pattern": r'(?i)\b(?:data protection officer|DPO|data privacy officer|privacy officer|appointed DPO)\b',
        "description": "Data Protection Officer Reference",
        "gdpr_articles": ["article_37", "article_38", "article_39"],
        "risk_level": "medium",
        "remediation": "Consider whether appointing a DPO is required for your organization",
        "gdpr_principle": "accountability"
    },
    "dpia": {
        "pattern": r'(?i)\b(?:data protection impact assessment|DPIA|impact assessment|risk assessment|privacy impact)\b',
        "description": "Data Protection Impact Assessment Reference",
        "gdpr_articles": ["article_35"],
        "risk_level": "high",
        "remediation": "Conduct DPIAs for high-risk processing activities",
        "gdpr_principle": "accountability"
    }
}

# Netherlands-specific UAVG Patterns (Dutch implementation of GDPR)
NL_UAVG_PATTERNS = {
    # Dutch-specific retention requirements
    "nl_retention_period": {
        "pattern": r'(?i)\b(?:bewaar(?:termijn|plicht)|bewaartermijnen|wettelijke bewaartermijn|fiscale bewaarplicht|administratieplicht)\b',
        "description": "Dutch Retention Period Requirements (UAVG)",
        "gdpr_articles": ["article_5_1_e"],
        "uavg_articles": ["article_46"],
        "risk_level": "high",
        "remediation": "Ensure compliance with Dutch specific retention periods (Fiscale Bewaarplicht 7 years, Medical data 15-20 years)",
        "gdpr_principle": "storage_limitation",
        "country_specific": "Netherlands"
    },
    # Dutch-specific BSN (Citizen Service Number) handling
    "nl_bsn_processing": {
        "pattern": r'(?i)\b(?:BSN|burgerservicenummer|sofinummer|persoonsnummer)\b',
        "description": "Dutch BSN Processing Rules (UAVG)",
        "gdpr_articles": ["article_9"],
        "uavg_articles": ["article_46"],
        "risk_level": "high",
        "remediation": "Process BSN only when legally authorized under Dutch law (UAVG article 46)",
        "gdpr_principle": "lawfulness_fairness_transparency",
        "country_specific": "Netherlands"
    },
    # Dutch-specific data breach notification requirements
    "nl_breach_notification": {
        "pattern": r'(?i)\b(?:datalek|data lek|meldplicht datalekken|AP melden|Autoriteit Persoonsgegevens|melden datalek)\b',
        "description": "Dutch Data Breach Notification Requirements (UAVG)",
        "gdpr_articles": ["article_33", "article_34"],
        "uavg_articles": ["article_33"],
        "risk_level": "high",
        "remediation": "Implement Dutch-specific data breach notification procedures (72-hour deadline to Dutch DPA)",
        "gdpr_principle": "integrity_confidentiality",
        "country_specific": "Netherlands"
    },
    # Dutch-specific data sharing regulations
    "nl_data_sharing": {
        "pattern": r'(?i)\b(?:gegevensuitwisseling|doorgifte gegevens|gegevens delen|delen van persoonsgegevens|internationale doorgifte)\b',
        "description": "Dutch Data Sharing Regulations (UAVG)",
        "gdpr_articles": ["article_44", "article_45", "article_46"],
        "uavg_articles": ["article_47"],
        "risk_level": "medium",
        "remediation": "Ensure compliance with Dutch-specific regulations for data sharing, particularly with non-EU countries",
        "gdpr_principle": "integrity_confidentiality",
        "country_specific": "Netherlands"
    },
    # Dutch DPA (Autoriteit Persoonsgegevens) specific requirements
    "nl_dpa_requirements": {
        "pattern": r'(?i)\b(?:Autoriteit Persoonsgegevens|AP|Dutch DPA|toezichthoudende autoriteit|CBP)\b',
        "description": "Dutch DPA Specific Requirements (UAVG)",
        "gdpr_articles": ["article_51", "article_57", "article_58"],
        "uavg_articles": ["article_6", "article_7", "article_15"],
        "risk_level": "medium",
        "remediation": "Follow Dutch DPA (Autoriteit Persoonsgegevens) specific guidelines and reporting requirements",
        "gdpr_principle": "accountability",
        "country_specific": "Netherlands"
    },
    # Dutch minors consent requirements (under 16 years)
    "nl_minor_consent": {
        "pattern": r'(?i)\b(?:minderjarig(?:e|en)?|leeftijdsverificatie|jonger dan 16|onder 16 jaar|leeftijdscontrole|ouderlijke toestemming|toestemming ouders)\b',
        "description": "Dutch Minor Consent Requirements (UAVG)",
        "gdpr_articles": ["article_8"],
        "uavg_articles": ["article_5"],
        "risk_level": "high",
        "remediation": "Implement age verification and parental consent for users under 16 years old as required by Dutch UAVG",
        "gdpr_principle": "lawfulness_fairness_transparency",
        "country_specific": "Netherlands"
    }
}

def map_finding_to_gdpr_articles(finding_type: str, finding_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Map a finding to relevant GDPR articles based on its type and content.
    
    Args:
        finding_type: Type of finding (e.g., 'pii', 'dsar', 'consent', 'security', 'principle')
        finding_data: Data about the finding
        
    Returns:
        List of dictionaries with GDPR article mappings
    """
    article_mappings = []
    pattern_key = finding_data.get('pattern_key', '')
    pattern_data = {}
    
    # Determine the pattern data based on finding type
    if finding_type == 'pii' and pattern_key in PII_PATTERNS:
        pattern_data = PII_PATTERNS[pattern_key]
    elif finding_type == 'dsar' and pattern_key in DSAR_PATTERNS:
        pattern_data = DSAR_PATTERNS[pattern_key]
    elif finding_type == 'consent' and pattern_key in CONSENT_PATTERNS:
        pattern_data = CONSENT_PATTERNS[pattern_key]
    elif finding_type == 'security' and pattern_key in SECURITY_PATTERNS:
        pattern_data = SECURITY_PATTERNS[pattern_key]
    elif finding_type == 'principle' and pattern_key in GDPR_PRINCIPLE_PATTERNS:
        pattern_data = GDPR_PRINCIPLE_PATTERNS[pattern_key]
    
    # If we have pattern data with GDPR article mappings
    if pattern_data and 'gdpr_articles' in pattern_data:
        for article_key in pattern_data['gdpr_articles']:
            if article_key in GDPR_ARTICLES:
                article_info = GDPR_ARTICLES[article_key].copy()
                article_info['finding_type'] = finding_type
                article_info['pattern_key'] = pattern_key
                article_mappings.append(article_info)
    
    return article_mappings

def generate_remediation_suggestion(finding: Dict[str, Any]) -> str:
    """
    Generate a specific remediation suggestion based on the finding.
    
    Args:
        finding: The finding data including type, pattern, etc.
        
    Returns:
        Remediation suggestion string
    """
    finding_type = finding.get('type', '')
    pattern_key = finding.get('pattern_key', '')
    
    # Get the relevant patterns dictionary based on finding type
    patterns_dict = None
    if finding_type == 'pii':
        patterns_dict = PII_PATTERNS
    elif finding_type == 'dsar':
        patterns_dict = DSAR_PATTERNS
    elif finding_type == 'consent':
        patterns_dict = CONSENT_PATTERNS
    elif finding_type == 'security':
        patterns_dict = SECURITY_PATTERNS
    elif finding_type == 'principle':
        patterns_dict = GDPR_PRINCIPLE_PATTERNS
    elif finding_type == 'nl_uavg':
        patterns_dict = NL_UAVG_PATTERNS
    
    # Get the pattern-specific remediation if available
    if patterns_dict and pattern_key in patterns_dict and 'remediation' in patterns_dict[pattern_key]:
        return patterns_dict[pattern_key]['remediation']
    
    # Check GDPR principle if it exists
    gdpr_principle = finding.get('gdpr_principle', '')
    if gdpr_principle:
        principle_recommendations = {
            'lawfulness_fairness_transparency': "Ensure lawful processing with a documented legal basis, fair data handling, and transparent information to data subjects.",
            'purpose_limitation': "Clearly define and document specific purposes for data processing and prevent usage beyond those purposes.",
            'data_minimization': "Collect and process only the data necessary for your specified purposes, and delete unnecessary data.",
            'accuracy': "Implement mechanisms to ensure personal data is accurate and up-to-date, with processes for correction.",
            'storage_limitation': "Define appropriate retention periods and implement processes to delete data once no longer needed.",
            'integrity_confidentiality': "Implement appropriate security measures to protect data from unauthorized access, loss, or damage.",
            'accountability': "Document compliance measures and be able to demonstrate compliance with all GDPR principles."
        }
        if gdpr_principle in principle_recommendations:
            return principle_recommendations[gdpr_principle]
    
    # Check for country-specific recommendations
    country_specific = finding.get('country_specific', '')
    if country_specific == 'Netherlands':
        # Specific Dutch UAVG remediation suggestions based on pattern key
        if pattern_key.startswith('nl_'):
            nl_specific_recommendations = {
                'nl_retention_period': "Ensure compliance with Dutch retention requirements: fiscal data (7 years), medical data (15-20 years), client identity (5 years), and employment data (2-5 years).",
                'nl_bsn_processing': "Process BSN (Dutch citizen service number) only when explicitly authorized by law, such as employment, taxation, or social security purposes.",
                'nl_breach_notification': "Implement Dutch-specific breach notification procedures, including the 72-hour deadline for reporting to Autoriteit Persoonsgegevens.",
                'nl_data_sharing': "Review and ensure compliance with Dutch regulations for international data transfers, especially when sharing data outside the EU.",
                'nl_dpa_requirements': "Follow Autoriteit Persoonsgegevens (Dutch DPA) guidelines and ensure appropriate reporting mechanisms are in place.",
                'nl_minor_consent': "Implement age verification and parental consent collection for users under 16 years old as required by Dutch UAVG (Article 5)."
            }
            if pattern_key in nl_specific_recommendations:
                return nl_specific_recommendations[pattern_key]
            
    # Default remediation suggestions by finding type
    default_remediation = {
        'pii': "Ensure proper legal basis and implement data protection measures for handling personal data.",
        'dsar': "Implement proper procedures for handling data subject rights requests.",
        'consent': "Ensure explicit, informed consent is collected and properly recorded.",
        'security': "Implement appropriate technical and organizational security measures.",
        'principle': "Implement measures to ensure compliance with this GDPR principle.",
        'nl_uavg': "Ensure compliance with Netherlands-specific UAVG requirements which implement GDPR in Dutch law."
    }
    
    return default_remediation.get(finding_type, "Review this finding for GDPR compliance.")

def calculate_gdpr_risk_score(findings: List[Dict[str, Any]]) -> Tuple[float, Dict[str, float]]:
    """
    Calculate a GDPR compliance risk score based on findings.
    
    Args:
        findings: List of findings with risk levels
        
    Returns:
        Tuple of (total_score, score_breakdown)
    """
    # Risk level weights
    risk_weights = {
        'low': 1,
        'medium': 3,
        'high': 5,
        'critical': 10
    }
    
    # Article weights (some articles carry more compliance importance)
    article_weights = {
        'article_6_1_a': 1.5,  # Consent is critical
        'article_32': 1.5,     # Security measures are critical
        'article_17': 1.2,     # Right to erasure is important
        'article_25': 1.2,     # Data protection by design is important
        'article_15': 1.2,     # Right of access is important
        'default': 1.0         # Default weight
    }
    
    # Initialize score and breakdown
    total_score = 0.0
    score_breakdown = {
        'pii': 0.0,
        'dsar': 0.0,
        'consent': 0.0,
        'security': 0.0,
        'principle': 0.0,
        'nl_uavg': 0.0,
        'other': 0.0
    }
    
    # Process each finding
    for finding in findings:
        finding_type = finding.get('type', 'other')
        risk_level = finding.get('risk_level', 'low')
        
        # Get the risk weight
        risk_weight = risk_weights.get(risk_level, 1)
        
        # Get article references to apply article weights
        article_refs = finding.get('gdpr_articles', [])
        
        # If no specific articles, use default weight
        if not article_refs:
            article_multiplier = article_weights['default']
        else:
            # Use the highest article weight for any referenced articles
            article_multiplier = max(article_weights.get(ref, article_weights['default']) for ref in article_refs)
        
        # Calculate this finding's score contribution
        finding_score = risk_weight * article_multiplier
        
        # Add to total and breakdown
        total_score += finding_score
        
        # Add to appropriate category in breakdown
        if finding_type in score_breakdown:
            score_breakdown[finding_type] += finding_score
        else:
            score_breakdown['other'] += finding_score
    
    return total_score, score_breakdown

def calculate_compliance_score(risk_score: float, max_score: int = 100) -> int:
    """
    Convert a risk score to a compliance score (higher is better).
    
    Args:
        risk_score: The calculated risk score
        max_score: The maximum possible compliance score
        
    Returns:
        Compliance score as an integer (0-100)
    """
    # Normalize risk score to a baseline (assuming 50 is a typical maximum risk score)
    normalized_risk = min(risk_score / 50.0, 1.0)
    
    # Higher risk means lower compliance
    compliance_score = max_score * (1.0 - normalized_risk)
    
    # Ensure the score is between 0 and max_score
    compliance_score_int = int(compliance_score)
    return max(0, min(compliance_score_int, max_score))

def get_remediation_priority(finding: Dict[str, Any]) -> str:
    """
    Get the remediation priority for a finding based on risk level and GDPR article.
    
    Args:
        finding: The finding data
        
    Returns:
        Priority level ("high", "medium", or "low")
    """
    risk_level = finding.get('risk_level', 'low')
    article_refs = finding.get('gdpr_articles', [])
    uavg_article_refs = finding.get('uavg_articles', [])
    finding_type = finding.get('type', '')
    
    # Dutch-specific checks with high priority
    if finding_type == 'nl_uavg' and finding.get('country_specific', '') == 'Netherlands':
        # BSN processing, data breach notification, and minor consent are critical in Dutch context
        pattern_key = finding.get('pattern_key', '')
        if pattern_key in ['nl_bsn_processing', 'nl_breach_notification', 'nl_minor_consent']:
            return "high"
    
    # High risk findings always have high priority
    if risk_level == 'high' or risk_level == 'critical':
        return "high"
    
    # Check article references for high priority articles
    high_priority_articles = ['article_6_1_a', 'article_32', 'article_17', 'article_15']
    for article in article_refs:
        if article in high_priority_articles:
            return "high"
    
    # Dutch UAVG-specific prioritization
    if uavg_article_refs:
        high_priority_uavg_articles = ['article_46', 'article_5']  # Dutch BSN processing and minor consent articles
        for article in uavg_article_refs:
            if article in high_priority_uavg_articles:
                return "high"
    
    # Medium risk findings that aren't tied to high priority articles
    if risk_level == 'medium':
        return "medium"
    
    # Low risk findings
    return "low"
"""
GDPR Compliance Module

This module provides GDPR-specific patterns, article mappings, and compliance evaluation functions
to enhance repository scanning with proper GDPR legal basis identification and risk assessment.
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
        "remediation": "Ensure sensitive data is encrypted at rest and in transit"
    },
    "pseudonymization": {
        "pattern": r'(?i)\b(?:pseudonymize|pseudonymization|anonymize|anonymization|data masking)\b',
        "description": "Pseudonymization Implementation",
        "gdpr_articles": ["article_32", "article_25"],
        "risk_level": "medium",
        "remediation": "Implement pseudonymization for personal data where appropriate"
    },
    "data_breach": {
        "pattern": r'(?i)\b(?:data breach|security incident|breach notification|incident response)\b',
        "description": "Data Breach Handling",
        "gdpr_articles": ["article_33", "article_34"],
        "risk_level": "high",
        "remediation": "Implement data breach detection and notification procedures"
    }
}

def map_finding_to_gdpr_articles(finding_type: str, finding_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Map a finding to relevant GDPR articles based on its type and content.
    
    Args:
        finding_type: Type of finding (e.g., 'pii', 'dsar', 'consent', 'security')
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
    
    # Get the pattern-specific remediation if available
    if patterns_dict and pattern_key in patterns_dict and 'remediation' in patterns_dict[pattern_key]:
        return patterns_dict[pattern_key]['remediation']
    
    # Default remediation suggestions by finding type
    default_remediation = {
        'pii': "Ensure proper legal basis and implement data protection measures for handling personal data.",
        'dsar': "Implement proper procedures for handling data subject rights requests.",
        'consent': "Ensure explicit, informed consent is collected and properly recorded.",
        'security': "Implement appropriate technical and organizational security measures."
    }
    
    return default_remediation.get(finding_type, "Review this finding for GDPR compliance.")

def calculate_gdpr_risk_score(findings: List[Dict[str, Any]]) -> Tuple[int, Dict[str, int]]:
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
    total_score = 0
    score_breakdown = {
        'pii': 0,
        'dsar': 0,
        'consent': 0,
        'security': 0,
        'other': 0
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

def calculate_compliance_score(risk_score: float, max_score: float = 100) -> int:
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
    return max(0, min(int(compliance_score), max_score))

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
    
    # High risk findings always have high priority
    if risk_level == 'high' or risk_level == 'critical':
        return "high"
    
    # Check article references for high priority articles
    high_priority_articles = ['article_6_1_a', 'article_32', 'article_17', 'article_15']
    for article in article_refs:
        if article in high_priority_articles:
            return "high"
    
    # Medium risk findings that aren't tied to high priority articles
    if risk_level == 'medium':
        return "medium"
    
    # Low risk findings
    return "low"
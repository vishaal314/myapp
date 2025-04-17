from typing import Dict, List, Any

# Define regions and their rules
REGIONS = {
    "Netherlands": {
        "bsn_required": True,
        "minor_age_limit": 16,
        "breach_notification_hours": 72,
        "high_risk_pii": ["BSN", "Medical Data", "Credit Card", "Passport Number"],
        "medium_risk_pii": ["Date of Birth", "Address", "Phone", "Financial Data"],
        "low_risk_pii": ["Name", "Email", "IP Address", "Username"]
    },
    "Germany": {
        "bsn_required": False,
        "minor_age_limit": 16,
        "breach_notification_hours": 72,
        "high_risk_pii": ["Medical Data", "Credit Card", "Passport Number"],
        "medium_risk_pii": ["Date of Birth", "Address", "Phone", "Financial Data"],
        "low_risk_pii": ["Name", "Email", "IP Address", "Username"]
    },
    "France": {
        "bsn_required": False,
        "minor_age_limit": 15,
        "breach_notification_hours": 72,
        "high_risk_pii": ["Medical Data", "Credit Card", "Passport Number"],
        "medium_risk_pii": ["Date of Birth", "Address", "Phone", "Financial Data"],
        "low_risk_pii": ["Name", "Email", "IP Address", "Username"]
    },
    "Belgium": {
        "bsn_required": False,
        "minor_age_limit": 13,
        "breach_notification_hours": 72,
        "high_risk_pii": ["Medical Data", "Credit Card", "Passport Number"],
        "medium_risk_pii": ["Date of Birth", "Address", "Phone", "Financial Data"],
        "low_risk_pii": ["Name", "Email", "IP Address", "Username"]
    }
}

def get_region_rules(region: str) -> Dict[str, Any]:
    """
    Get the GDPR rules for a specific region.
    
    Args:
        region: The region name
        
    Returns:
        Dictionary of region-specific GDPR rules
    """
    if region in REGIONS:
        return REGIONS[region]
    
    # Default to Netherlands if region not found
    return REGIONS["Netherlands"]

def evaluate_risk_level(pii_type: str, region_rules: Dict[str, Any]) -> str:
    """
    Evaluate the risk level of a PII type based on region rules.
    
    Args:
        pii_type: The type of PII
        region_rules: The region-specific GDPR rules
        
    Returns:
        Risk level: "High", "Medium", or "Low"
    """
    if pii_type in region_rules.get("high_risk_pii", []):
        return "High"
    elif pii_type in region_rules.get("medium_risk_pii", []):
        return "Medium"
    elif pii_type in region_rules.get("low_risk_pii", []):
        return "Low"
    
    # Default to Medium if not explicitly categorized
    return "Medium"

def requires_consent_for_minors(pii_type: str, region_rules: Dict[str, Any]) -> bool:
    """
    Check if the PII type requires consent for minors.
    
    Args:
        pii_type: The type of PII
        region_rules: The region-specific GDPR rules
        
    Returns:
        True if consent is required, False otherwise
    """
    # All high-risk PII requires consent for minors
    if pii_type in region_rules.get("high_risk_pii", []):
        return True
    
    # Specific PII types that always require consent for minors
    consent_required_types = ["Date of Birth", "Email", "Phone", "Address", "Photo", "Medical Data"]
    return pii_type in consent_required_types

def requires_dpia(pii_types: List[str], region_rules: Dict[str, Any]) -> bool:
    """
    Check if a Data Protection Impact Assessment (DPIA) is required.
    
    Args:
        pii_types: List of PII types found
        region_rules: The region-specific GDPR rules
        
    Returns:
        True if a DPIA is required, False otherwise
    """
    high_risk_count = sum(1 for pii_type in pii_types if pii_type in region_rules.get("high_risk_pii", []))
    
    # DPIA is required if there are more than 2 different high-risk PII types
    if high_risk_count > 2:
        return True
    
    # DPIA is required for specific high-risk PII types regardless of count
    special_categories = ["Medical Data", "Genetic Data", "Biometric Data"]
    for pii_type in pii_types:
        if pii_type in special_categories:
            return True
    
    return False

def get_legal_basis_options(pii_type: str, region_rules: Dict[str, Any]) -> List[str]:
    """
    Get possible legal bases for processing a specific PII type.
    
    Args:
        pii_type: The type of PII
        region_rules: The region-specific GDPR rules
        
    Returns:
        List of possible legal bases
    """
    # Default legal bases under GDPR Article 6
    default_bases = [
        "Consent",
        "Contract",
        "Legal Obligation",
        "Vital Interests",
        "Public Interest",
        "Legitimate Interests"
    ]
    
    # Special category data (Article 9) has more restricted legal bases
    special_categories = ["Medical Data", "Genetic Data", "Biometric Data", "Religious Beliefs", "Political Opinions"]
    
    if pii_type in special_categories:
        return [
            "Explicit Consent",
            "Employment/Social Security Law",
            "Vital Interests (unable to consent)",
            "Non-profit Organizations (members only)",
            "Data Made Public by the Subject",
            "Legal Claims",
            "Public Interest (substantial)",
            "Preventive/Occupational Medicine",
            "Public Health",
            "Archiving/Research"
        ]
    
    return default_bases

def get_breach_notification_requirement(region: str) -> Dict[str, Any]:
    """
    Get breach notification requirements for a region.
    
    Args:
        region: The region name
        
    Returns:
        Dictionary with breach notification requirements
    """
    region_rules = get_region_rules(region)
    
    return {
        "supervisory_authority_hours": region_rules.get("breach_notification_hours", 72),
        "data_subject_required": "without undue delay",
        "documentation_required": True,
        "risk_assessment_required": True
    }

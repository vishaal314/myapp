"""
GDPR Risk Categories

Standardized risk categories and mapping functions for GDPR compliance scanning.
This ensures consistent risk categorization across the system.
"""

from enum import Enum
from typing import Dict, Any, List, Optional

# Define standard risk levels
class RiskLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NONE = "None"

# Define standard severity levels (used internally)
class SeverityLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

# Define standard remediation priorities
class RemediationPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

# Define weights for risk calculation
RISK_WEIGHTS = {
    RiskLevel.HIGH: 5,
    RiskLevel.MEDIUM: 3,
    RiskLevel.LOW: 1,
    RiskLevel.NONE: 0
}

# Define maximum compliance score
MAX_COMPLIANCE_SCORE = 100

# Define compliance status thresholds
COMPLIANCE_STATUS_THRESHOLDS = {
    90: "Compliant",
    70: "Largely Compliant",
    50: "Needs Improvement",
    0: "Non-Compliant"
}

def map_severity_to_risk_level(severity: str) -> str:
    """
    Map a severity level to a standardized risk level.
    
    Args:
        severity: Severity level string
        
    Returns:
        Standardized risk level string
    """
    severity_mapping = {
        SeverityLevel.HIGH.value: RiskLevel.HIGH.value,
        SeverityLevel.MEDIUM.value: RiskLevel.MEDIUM.value,
        SeverityLevel.LOW.value: RiskLevel.LOW.value,
        SeverityLevel.NONE.value: RiskLevel.NONE.value,
    }
    
    # Default to Medium if unknown severity level
    return severity_mapping.get(severity.lower(), RiskLevel.MEDIUM.value)

def map_severity_to_priority(severity: str) -> str:
    """
    Map a severity level to a remediation priority.
    
    Args:
        severity: Severity level string
        
    Returns:
        Remediation priority string
    """
    severity_mapping = {
        SeverityLevel.HIGH.value: RemediationPriority.HIGH.value,
        SeverityLevel.MEDIUM.value: RemediationPriority.MEDIUM.value,
        SeverityLevel.LOW.value: RemediationPriority.LOW.value,
        SeverityLevel.NONE.value: RemediationPriority.NONE.value,
    }
    
    # Default to Medium if unknown severity level
    return severity_mapping.get(severity.lower(), RemediationPriority.MEDIUM.value)

def validate_risk_level(risk_level: str) -> str:
    """
    Validate and normalize a risk level string.
    
    Args:
        risk_level: Risk level string to validate
        
    Returns:
        Normalized risk level string
        
    Raises:
        ValueError: If risk level is invalid
    """
    normalized = risk_level.strip().capitalize()
    valid_levels = [level.value for level in RiskLevel]
    
    if normalized not in valid_levels:
        raise ValueError(f"Invalid risk level: {risk_level}. Must be one of {valid_levels}")
    
    return normalized

def calculate_compliance_score(risk_counts: Dict[str, int]) -> int:
    """
    Calculate a compliance score based on risk counts.
    
    Args:
        risk_counts: Dictionary mapping risk levels to counts
        
    Returns:
        Compliance score (0-100)
    """
    # Normalize risk counts
    normalized_counts = {
        RiskLevel.HIGH.value: risk_counts.get(RiskLevel.HIGH.value, 0),
        RiskLevel.MEDIUM.value: risk_counts.get(RiskLevel.MEDIUM.value, 0),
        RiskLevel.LOW.value: risk_counts.get(RiskLevel.LOW.value, 0),
    }
    
    # Calculate weighted issue points
    issue_points = sum([
        normalized_counts[RiskLevel.HIGH.value] * RISK_WEIGHTS[RiskLevel.HIGH],
        normalized_counts[RiskLevel.MEDIUM.value] * RISK_WEIGHTS[RiskLevel.MEDIUM],
        normalized_counts[RiskLevel.LOW.value] * RISK_WEIGHTS[RiskLevel.LOW],
    ])
    
    # Calculate compliance score
    compliance_score = max(0, MAX_COMPLIANCE_SCORE - min(issue_points, MAX_COMPLIANCE_SCORE))
    
    return round(compliance_score)

def determine_compliance_status(compliance_score: float) -> str:
    """
    Determine compliance status based on compliance score.
    
    Args:
        compliance_score: Compliance score (0-100)
        
    Returns:
        Compliance status string
    """
    for threshold, status in sorted(COMPLIANCE_STATUS_THRESHOLDS.items(), reverse=True):
        if compliance_score >= threshold:
            return status
    
    # Default status if no thresholds matched (should never happen with current thresholds)
    return "Non-Compliant"

def normalize_risk_counts(risk_counts: Dict[str, int]) -> Dict[str, int]:
    """
    Normalize risk counts to ensure consistent structure.
    
    Args:
        risk_counts: Dictionary mapping risk levels to counts
        
    Returns:
        Normalized risk counts dictionary
    """
    return {
        RiskLevel.HIGH.value: risk_counts.get(RiskLevel.HIGH.value, 0),
        RiskLevel.MEDIUM.value: risk_counts.get(RiskLevel.MEDIUM.value, 0),
        RiskLevel.LOW.value: risk_counts.get(RiskLevel.LOW.value, 0),
    }

def merge_risk_counts(original_counts: Dict[str, int], enhanced_counts: Dict[str, int]) -> Dict[str, int]:
    """
    Merge risk counts from multiple sources with normalization.
    
    Args:
        original_counts: Original risk counts
        enhanced_counts: Enhanced risk counts
        
    Returns:
        Merged risk counts
    """
    # Normalize input counts
    norm_original = normalize_risk_counts(original_counts)
    norm_enhanced = normalize_risk_counts(enhanced_counts)
    
    # Merge counts
    merged_counts = {
        RiskLevel.HIGH.value: norm_original.get(RiskLevel.HIGH.value, 0) + norm_enhanced.get(RiskLevel.HIGH.value, 0),
        RiskLevel.MEDIUM.value: norm_original.get(RiskLevel.MEDIUM.value, 0) + norm_enhanced.get(RiskLevel.MEDIUM.value, 0),
        RiskLevel.LOW.value: norm_original.get(RiskLevel.LOW.value, 0) + norm_enhanced.get(RiskLevel.LOW.value, 0),
    }
    
    return merged_counts
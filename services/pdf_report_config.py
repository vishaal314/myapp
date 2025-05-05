"""
PDF Report Configuration

This module provides configuration settings for PDF reports, 
ensuring consistent risk level representation across all report formats.
"""

from typing import Dict, Any
from services.gdpr_risk_categories import RiskLevel

# Define risk level colors for PDF reports
RISK_LEVEL_COLORS = {
    RiskLevel.HIGH.value: "#EF4444",  # Red
    RiskLevel.MEDIUM.value: "#F97316",  # Orange
    RiskLevel.LOW.value: "#10B981",  # Green
    RiskLevel.NONE.value: "#9CA3AF"   # Grey
}

# Define risk level icons for PDF reports
RISK_LEVEL_ICONS = {
    RiskLevel.HIGH.value: "⚠️",  # Warning sign
    RiskLevel.MEDIUM.value: "⚠",  # Warning
    RiskLevel.LOW.value: "ℹ️",  # Info
    RiskLevel.NONE.value: "✓"   # Checkmark
}

# Define risk level display names for PDF reports
RISK_LEVEL_DISPLAY_NAMES = {
    RiskLevel.HIGH.value: "Critical",
    RiskLevel.MEDIUM.value: "Warning",
    RiskLevel.LOW.value: "Info",
    RiskLevel.NONE.value: "Pass"
}

# Define risk level heading names for PDF reports
RISK_LEVEL_HEADINGS = {
    RiskLevel.HIGH.value: "High Risk Items",
    RiskLevel.MEDIUM.value: "Medium Risk Items", 
    RiskLevel.LOW.value: "Low Risk Items",
    RiskLevel.NONE.value: "Passed Checks"
}

# Define compliance status colors for PDF reports
COMPLIANCE_STATUS_COLORS = {
    "Compliant": "#10B981",           # Green
    "Largely Compliant": "#22D3EE",   # Blue
    "Needs Improvement": "#F97316",   # Orange
    "Non-Compliant": "#EF4444"        # Red
}

# Define remediation priority colors for PDF reports
REMEDIATION_PRIORITY_COLORS = {
    "high": "#EF4444",    # Red
    "medium": "#F97316",  # Orange
    "low": "#10B981"      # Green
}

def get_risk_level_style(risk_level: str) -> Dict[str, Any]:
    """
    Get the style configuration for a risk level.
    
    Args:
        risk_level: Risk level string
        
    Returns:
        Dictionary with style configuration
    """
    # Normalize risk level
    normalized_risk = risk_level if risk_level in RISK_LEVEL_COLORS else RiskLevel.MEDIUM.value
    
    return {
        "color": RISK_LEVEL_COLORS.get(normalized_risk, RISK_LEVEL_COLORS[RiskLevel.MEDIUM.value]),
        "icon": RISK_LEVEL_ICONS.get(normalized_risk, RISK_LEVEL_ICONS[RiskLevel.MEDIUM.value]),
        "display_name": RISK_LEVEL_DISPLAY_NAMES.get(normalized_risk, RISK_LEVEL_DISPLAY_NAMES[RiskLevel.MEDIUM.value]),
        "heading": RISK_LEVEL_HEADINGS.get(normalized_risk, RISK_LEVEL_HEADINGS[RiskLevel.MEDIUM.value])
    }

def get_compliance_status_color(status: str) -> str:
    """
    Get the color for a compliance status.
    
    Args:
        status: Compliance status string
        
    Returns:
        Color hex code
    """
    return COMPLIANCE_STATUS_COLORS.get(status, COMPLIANCE_STATUS_COLORS["Needs Improvement"])

def get_remediation_priority_color(priority: str) -> str:
    """
    Get the color for a remediation priority.
    
    Args:
        priority: Remediation priority string
        
    Returns:
        Color hex code
    """
    return REMEDIATION_PRIORITY_COLORS.get(priority, REMEDIATION_PRIORITY_COLORS["medium"])
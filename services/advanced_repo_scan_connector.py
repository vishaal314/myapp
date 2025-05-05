"""
Advanced Repository Scan Connector

This connector module bridges the enhanced GDPR article scanner with the main application.
It formats and processes results from the article-specific scanner to match the structure
expected by the main application.
"""

import logging
from typing import Dict, List, Any, Optional

from services.enhanced_gdpr_repo_scanner import GDPRArticleScanner
from services.gdpr_risk_categories import (
    RiskLevel, SeverityLevel, RemediationPriority,
    map_severity_to_risk_level, map_severity_to_priority,
    validate_risk_level, calculate_compliance_score, 
    determine_compliance_status
)

# Configure logging
logger = logging.getLogger(__name__)

def run_enhanced_gdpr_scan(repo_path: str) -> Dict[str, Any]:
    """
    Run an enhanced GDPR scan on a repository and format the results.
    
    Args:
        repo_path: Path to the repository directory
        
    Returns:
        Dictionary with formatted scan results
        
    Raises:
        RuntimeError: If scanning fails
    """
    try:
        # Initialize scanner
        scanner = GDPRArticleScanner(repo_path)
        
        # Run scan
        logger.info(f"Starting enhanced GDPR scan on repository: {repo_path}")
        scan_results = scanner.scan_repository()
        
        # Format results
        logger.info("Formatting enhanced GDPR scan results")
        formatted_results = _format_enhanced_results(scan_results)
        
        logger.info("Enhanced GDPR scan completed successfully")
        return formatted_results
    except Exception as e:
        logger.error(f"Error during enhanced GDPR scan: {str(e)}")
        raise RuntimeError(f"Enhanced GDPR scan failed: {str(e)}")

def _format_enhanced_results(scan_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format scanner results to match the structure expected by the main application.
    
    Args:
        scan_results: Raw scan results from GDPRArticleScanner
        
    Returns:
        Formatted scan results for the main application
    """
    # Validate input
    if not isinstance(scan_results, dict):
        raise ValueError("Invalid scan results format")
    
    if "findings" not in scan_results or "statistics" not in scan_results:
        raise ValueError("Missing required fields in scan results")
    
    # Extract findings and convert to application format
    formatted_findings = []
    for finding in scan_results["findings"]:
        formatted_finding = _format_finding(finding)
        formatted_findings.append(formatted_finding)
    
    # Extract statistics and convert to application format
    statistics = scan_results["statistics"]
    severity_counts = statistics.get("severity_counts", {})
    
    # Map severity counts to risk levels
    risk_counts = {
        RiskLevel.HIGH.value: severity_counts.get(SeverityLevel.HIGH.value, 0),
        RiskLevel.MEDIUM.value: severity_counts.get(SeverityLevel.MEDIUM.value, 0),
        RiskLevel.LOW.value: severity_counts.get(SeverityLevel.LOW.value, 0)
    }
    
    # Calculate risk breakdown by category
    risk_breakdown = _calculate_risk_breakdown(formatted_findings)
    
    # Build formatted results
    formatted_results = {
        "findings": formatted_findings,
        "statistics": {
            "total_files_scanned": statistics.get("total_files_scanned", 0),
            "total_findings": statistics.get("total_findings", 0),
            "scan_duration": statistics.get("scan_duration", 0)
        },
        "risk_summary": risk_counts,
        "gdpr_compliance": {
            "compliance_score": statistics.get("compliance_score", 0),
            "compliance_status": statistics.get("compliance_status", "Not Available"),
            "risk_breakdown": risk_breakdown,
            "remediation_priorities": _calculate_remediation_priorities(formatted_findings)
        }
    }
    
    return formatted_results

def _format_finding(finding: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a single finding to match the application's expected structure.
    
    Args:
        finding: Raw finding from GDPRArticleScanner
        
    Returns:
        Formatted finding for the main application
    """
    # Extract basic information
    article_id = finding.get("article_id", "unknown")
    severity = finding.get("severity", SeverityLevel.MEDIUM.value)
    principle = finding.get("principle", "Unknown Principle")
    
    # Map severity to risk level and remediation priority
    risk_level = map_severity_to_risk_level(severity)
    remediation_priority = map_severity_to_priority(severity)
    
    # Map article ID to GDPR article reference
    article_reference = _map_article_id_to_reference(article_id)
    
    # Create article mapping
    article_mapping = {
        "id": article_reference,
        "title": _get_article_title(article_id),
        "description": finding.get("message", "No description available"),
        "keywords": [],  # Would be populated from article metadata
        "remediation_priority": remediation_priority,
        "finding_type": _map_article_to_finding_type(article_id),
        "pattern_key": finding.get("pattern_key", "generic")
    }
    
    # Build formatted finding
    formatted_finding = {
        "type": _map_article_to_finding_type(article_id),
        "pattern_key": finding.get("pattern_key", "generic"),
        "value": finding.get("value", "N/A"),
        "location": finding.get("location", "Unknown Location"),
        "risk_level": risk_level,
        "description": principle,
        "gdpr_articles": [article_reference],
        "reason": finding.get("message", "No reason provided"),
        "remediation_priority": remediation_priority,
        "article_mappings": [article_mapping],
        "remediation": finding.get("remediation", "No remediation provided")
    }
    
    return formatted_finding

def _map_article_id_to_reference(article_id: str) -> str:
    """
    Map an article ID to a formal GDPR article reference.
    
    Args:
        article_id: Article ID (e.g., "article_5")
        
    Returns:
        Formal article reference (e.g., "Art. 5")
    """
    article_mapping = {
        "article_5": "Art. 5",
        "article_6": "Art. 6",
        "article_7": "Art. 7",
        "article_12_15": "Art. 12-15",
        "article_16_17": "Art. 16-17",
        "article_25": "Art. 25",
        "article_30": "Art. 30",
        "article_32": "Art. 32",
        "article_44_49": "Art. 44-49"
    }
    
    return article_mapping.get(article_id, "Unknown Article")

def _get_article_title(article_id: str) -> str:
    """
    Get the title for a GDPR article.
    
    Args:
        article_id: Article ID (e.g., "article_5")
        
    Returns:
        Article title
    """
    article_titles = {
        "article_5": "Principles Relating to Processing of Personal Data",
        "article_6": "Lawfulness of Processing",
        "article_7": "Conditions for Consent",
        "article_12_15": "Transparency and Data Subject Rights",
        "article_16_17": "Right to Rectification and Erasure",
        "article_25": "Data Protection by Design and by Default",
        "article_30": "Records of Processing Activities",
        "article_32": "Security of Processing",
        "article_44_49": "Transfers of Personal Data to Third Countries or International Organizations"
    }
    
    return article_titles.get(article_id, "Unknown Article")

def _map_article_to_finding_type(article_id: str) -> str:
    """
    Map a GDPR article to a finding type.
    
    Args:
        article_id: Article ID (e.g., "article_5")
        
    Returns:
        Finding type
    """
    article_to_type = {
        "article_5": "principle",
        "article_6": "legal_basis",
        "article_7": "consent",
        "article_12_15": "transparency",
        "article_16_17": "dsar",
        "article_25": "privacy_by_design",
        "article_30": "documentation",
        "article_32": "security",
        "article_44_49": "international_transfer"
    }
    
    return article_to_type.get(article_id, "gdpr")

def _calculate_risk_breakdown(findings: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate risk breakdown by finding type.
    
    Args:
        findings: List of formatted findings
        
    Returns:
        Dictionary mapping finding types to risk scores
    """
    # Initialize risk categories with float values
    risk_breakdown = {
        "pii": 0.0,
        "dsar": 0.0,
        "consent": 0.0,
        "security": 0.0,
        "principle": 0.0,
        "nl_uavg": 0.0,
        "other": 0.0
    }
    
    # Risk weights for calculation
    risk_weights = {
        RiskLevel.HIGH.value: 5.0,
        RiskLevel.MEDIUM.value: 3.0,
        RiskLevel.LOW.value: 1.0
    }
    
    # Calculate weighted risk score by category
    for finding in findings:
        finding_type = finding.get("type", "other")
        risk_level = finding.get("risk_level", RiskLevel.MEDIUM.value)
        
        # Get risk weight
        weight = risk_weights.get(risk_level, 3.0)
        
        # Update appropriate category
        if finding_type in risk_breakdown:
            risk_breakdown[finding_type] += weight
        else:
            risk_breakdown["other"] += weight
    
    # Round to one decimal place
    for key in risk_breakdown:
        risk_breakdown[key] = round(risk_breakdown[key], 1)
    
    return risk_breakdown

def _calculate_remediation_priorities(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate remediation priorities based on findings.
    
    Args:
        findings: List of formatted findings
        
    Returns:
        Dictionary mapping priority levels to counts
    """
    # Initialize priorities
    priorities = {
        "high": 0,
        "medium": 0,
        "low": 0
    }
    
    # Count findings by remediation priority
    for finding in findings:
        priority = finding.get("remediation_priority", "medium")
        if priority in priorities:
            priorities[priority] += 1
    
    return priorities
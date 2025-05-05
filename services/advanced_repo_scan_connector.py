"""
Advanced Repository Scanner Connector

This module connects the enhanced GDPR repository scanner to the main application,
integrating the article-specific findings with the existing scanning infrastructure.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional

from services.enhanced_gdpr_repo_scanner import scan_repository_for_gdpr_compliance

# Configure logging
logger = logging.getLogger(__name__)

def run_enhanced_gdpr_scan(repo_path: str) -> Dict[str, Any]:
    """
    Run an enhanced GDPR scan on a repository and format the results
    to integrate with the existing scanning infrastructure.
    
    Args:
        repo_path: Path to the repository directory
        
    Returns:
        Dictionary with formatted scan results
    """
    logger.info(f"Running enhanced GDPR scan on repository: {repo_path}")
    
    # Run the enhanced scanner
    enhanced_results = scan_repository_for_gdpr_compliance(repo_path)
    
    # Convert the enhanced results to the format expected by the main application
    formatted_results = _format_enhanced_results(enhanced_results)
    
    logger.info(f"Enhanced GDPR scan completed with {len(enhanced_results['findings'])} findings")
    return formatted_results

def _format_enhanced_results(enhanced_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the enhanced scanner results to match the format expected by the main application.
    
    Args:
        enhanced_results: Results from the enhanced scanner
        
    Returns:
        Formatted results compatible with the main application
    """
    findings = []
    
    # Convert each finding to the expected format
    for finding in enhanced_results['findings']:
        formatted_finding = {
            "type": _map_article_to_finding_type(finding["article_id"]),
            "value": _extract_value_from_finding(finding),
            "location": f"{finding['file_path']} (Line {finding['line_number']})",
            "risk_level": _map_severity_to_risk_level(finding["severity"]),
            "reason": finding["message"],
            "gdpr_articles": [_map_article_id_to_full_reference(finding["article_id"])],
            "remediation": finding["remediation"],
            "principle": finding["principle"],
            "snippet": finding["snippet"],
            "article_mappings": [{
                "id": _map_article_id_to_full_reference(finding["article_id"]),
                "title": finding["article_title"],
                "description": _get_article_description(finding["article_id"], finding["principle"]),
                "keywords": _get_article_keywords(finding["article_id"]),
                "remediation_priority": _map_severity_to_priority(finding["severity"]),
                "finding_type": _map_article_to_finding_type(finding["article_id"]),
                "pattern_key": _generate_pattern_key(finding)
            }]
        }
        
        findings.append(formatted_finding)
    
    # Prepare the formatted results
    formatted_results = {
        "findings": findings,
        "metadata": {
            "scanned_files": enhanced_results["scanned_files"],
            "total_findings": enhanced_results["total_findings"]
        },
        "risk_summary": {
            "High": enhanced_results["severity_counts"]["high"],
            "Medium": enhanced_results["severity_counts"]["medium"],
            "Low": enhanced_results["severity_counts"]["low"]
        },
        "gdpr_compliance": {
            "compliance_score": enhanced_results["compliance_score"],
            "risk_score": 100 - enhanced_results["compliance_score"],
            "risk_breakdown": _calculate_risk_breakdown(enhanced_results),
            "compliance_status": _determine_compliance_status(enhanced_results["compliance_score"]),
            "legal_basis_count": _count_legal_basis_findings(enhanced_results),
            "remediation_priorities": {
                "high": enhanced_results["severity_counts"]["high"],
                "medium": enhanced_results["severity_counts"]["medium"],
                "low": enhanced_results["severity_counts"]["low"]
            }
        },
        "article_findings": _group_findings_by_article(enhanced_results["findings_by_article"])
    }
    
    return formatted_results

def _map_article_to_finding_type(article_id: str) -> str:
    """
    Map a GDPR article ID to a finding type.
    
    Args:
        article_id: GDPR article ID
        
    Returns:
        Finding type string
    """
    article_type_mapping = {
        "article_5": "gdpr_principle",
        "article_6": "legal_basis",
        "article_7": "consent",
        "article_12_15": "transparency",
        "article_16_17": "data_subject_rights",
        "article_25": "privacy_by_design",
        "article_30": "processing_records",
        "article_32": "security",
        "article_44_49": "data_transfer"
    }
    
    return article_type_mapping.get(article_id, "gdpr_compliance")

def _extract_value_from_finding(finding: Dict[str, Any]) -> str:
    """
    Extract a representative value from a finding for display.
    
    Args:
        finding: Finding dictionary
        
    Returns:
        Value string for display
    """
    # Extract code snippet or meaningful value
    # This is a simplified approach - in production, more advanced extraction would be used
    snippet_lines = finding.get("snippet", "").split("\n")
    if len(snippet_lines) > 0:
        # Get the middle line (the one with the match)
        if len(snippet_lines) % 2 == 1:
            return snippet_lines[len(snippet_lines) // 2]
        else:
            return snippet_lines[len(snippet_lines) // 2 - 1]
    
    return finding.get("message", "GDPR compliance issue")

def _map_severity_to_risk_level(severity: str) -> str:
    """
    Map a severity level to a risk level.
    
    Args:
        severity: Severity string
        
    Returns:
        Risk level string
    """
    severity_mapping = {
        "high": "High",
        "medium": "Medium",
        "low": "Low"
    }
    
    return severity_mapping.get(severity, "Medium")

def _map_article_id_to_full_reference(article_id: str) -> str:
    """
    Map an article ID to a full GDPR article reference.
    
    Args:
        article_id: Article ID
        
    Returns:
        Full article reference string
    """
    article_reference_mapping = {
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
    
    return article_reference_mapping.get(article_id, "GDPR")

def _get_article_description(article_id: str, principle: str) -> str:
    """
    Get a description for a GDPR article and principle.
    
    Args:
        article_id: Article ID
        principle: Specific principle within the article
        
    Returns:
        Description string
    """
    # This would be more comprehensive in production
    article_descriptions = {
        "article_5": {
            "Lawfulness, Fairness, and Transparency": "Processing must be lawful, fair, and transparent to the data subject.",
            "Purpose Limitation": "Data must be collected for specified, explicit, and legitimate purposes.",
            "Data Minimization": "Data must be adequate, relevant, and limited to what is necessary.",
            "Accuracy": "Data must be accurate and kept up to date.",
            "Storage Limitation": "Data must be kept in a form that permits identification for no longer than necessary.",
            "Integrity and Confidentiality": "Data must be processed with appropriate security.",
            "Accountability": "The controller must be able to demonstrate compliance."
        },
        "article_6": {
            "Lawfulness of Processing": "Processing is lawful only if at least one legal basis applies.",
            "Consent": "The data subject has given consent for specific purposes.",
            "Contract Performance": "Processing is necessary for contract performance.",
            "Legal Obligation": "Processing is necessary for compliance with a legal obligation.",
            "Vital Interests": "Processing is necessary to protect vital interests.",
            "Public Interest": "Processing is necessary for a task in the public interest.",
            "Legitimate Interests": "Processing is necessary for legitimate interests."
        },
        "article_7": {
            "Demonstrable Consent": "The controller must be able to demonstrate consent.",
            "Clear Request": "Consent request must be in clear and plain language.",
            "Right to Withdraw": "The data subject has the right to withdraw consent.",
            "Freely Given": "Consent must be freely given and not conditional."
        },
        "article_12_15": {
            "Transparent Information": "Information must be provided in a concise, transparent, intelligible, and easily accessible form.",
            "Access to Data": "Data subjects have the right to access their personal data.",
            "Processing Information": "Information about processing must be provided.",
            "Recipients Disclosure": "Recipients of personal data must be disclosed."
        },
        "article_16_17": {
            "Rectification of Inaccurate Data": "Data subjects have the right to rectification of inaccurate data.",
            "Completion of Incomplete Data": "Data subjects have the right to have incomplete data completed.",
            "Erasure (Right to be Forgotten)": "Data subjects have the right to erasure of their data.",
            "Data Deletion": "Personal data must be deleted upon request when conditions are met."
        },
        "article_25": {
            "Privacy by Design": "Data protection measures must be designed into systems from the start.",
            "Privacy by Default": "By default, only personal data necessary for a specific purpose should be processed.",
            "Data Minimization": "Systems must be designed to minimize data collection.",
            "Pseudonymization": "Personal data should be pseudonymized where possible."
        },
        "article_30": {
            "Processing Records": "Records of processing activities must be maintained.",
            "Purpose Documentation": "Purposes of processing must be documented.",
            "Categories Documentation": "Categories of data and data subjects must be documented.",
            "Recipient Documentation": "Recipients of data must be documented."
        },
        "article_32": {
            "Encryption": "Personal data should be encrypted where appropriate.",
            "Confidentiality": "Processing systems must ensure confidentiality.",
            "Integrity": "Processing systems must ensure integrity.",
            "Availability": "Processing systems must ensure availability and resilience.",
            "Resilience": "Systems must be resilient to security incidents.",
            "Testing": "Security measures must be regularly tested.",
            "Risk Assessment": "Technical and organizational measures must be appropriate to the risk."
        },
        "article_44_49": {
            "International Transfers": "Transfers to third countries must have appropriate safeguards.",
            "Adequacy Decision": "Transfers can be based on an adequacy decision.",
            "Appropriate Safeguards": "Transfers must have appropriate safeguards.",
            "Binding Corporate Rules": "Transfers can be based on binding corporate rules.",
            "Standard Contractual Clauses": "Transfers can be based on standard contractual clauses.",
            "Explicit Consent for Transfer": "Transfers can be based on explicit consent."
        }
    }
    
    # Get the description for the article and principle
    if article_id in article_descriptions and principle in article_descriptions[article_id]:
        return article_descriptions[article_id][principle]
    
    # Fallback description
    fallback_descriptions = {
        "article_5": "Principles relating to processing of personal data",
        "article_6": "Lawfulness of processing",
        "article_7": "Conditions for consent",
        "article_12_15": "Transparency and rights of the data subject",
        "article_16_17": "Right to rectification and erasure",
        "article_25": "Data protection by design and by default",
        "article_30": "Records of processing activities",
        "article_32": "Security of processing",
        "article_44_49": "Transfers of personal data to third countries or international organizations"
    }
    
    return fallback_descriptions.get(article_id, "GDPR compliance requirement")

def _get_article_keywords(article_id: str) -> List[str]:
    """
    Get keywords associated with a GDPR article.
    
    Args:
        article_id: Article ID
        
    Returns:
        List of keyword strings
    """
    article_keywords = {
        "article_5": ["personal data", "processing", "purpose", "minimization", "accuracy", "storage", "security", "accountability"],
        "article_6": ["lawfulness", "consent", "contract", "legal obligation", "vital interests", "public interest", "legitimate interests"],
        "article_7": ["consent", "withdraw", "demonstrate", "clear", "freely given", "explicit"],
        "article_12_15": ["transparency", "information", "access", "communication", "notification"],
        "article_16_17": ["rectification", "erasure", "right to be forgotten", "deletion", "restriction"],
        "article_25": ["privacy by design", "privacy by default", "data protection", "data minimization", "pseudonymization"],
        "article_30": ["records", "processing activities", "documentation", "controller", "processor"],
        "article_32": ["security", "encryption", "confidentiality", "integrity", "availability", "resilience", "testing"],
        "article_44_49": ["transfers", "third country", "international organization", "adequacy", "safeguards", "binding corporate rules", "standard contractual clauses"]
    }
    
    return article_keywords.get(article_id, ["gdpr", "compliance"])

def _map_severity_to_priority(severity: str) -> str:
    """
    Map a severity level to a remediation priority.
    
    Args:
        severity: Severity string
        
    Returns:
        Priority string
    """
    severity_mapping = {
        "high": "high",
        "medium": "medium",
        "low": "low"
    }
    
    return severity_mapping.get(severity, "medium")

def _generate_pattern_key(finding: Dict[str, Any]) -> str:
    """
    Generate a unique pattern key for a finding.
    
    Args:
        finding: Finding dictionary
        
    Returns:
        Pattern key string
    """
    # This is a simplified approach - in production, more robust key generation would be used
    article_short = finding["article_id"].replace("article_", "")
    principle_key = "_".join(finding["principle"].lower().split())
    
    return f"{article_short}_{principle_key}"

def _calculate_risk_breakdown(enhanced_results: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate a risk breakdown for the enhanced results.
    
    Args:
        enhanced_results: Enhanced scanner results
        
    Returns:
        Dictionary with risk breakdown by category
    """
    # Count findings by article
    article_counts = {}
    for finding in enhanced_results["findings"]:
        article_id = finding["article_id"]
        if article_id not in article_counts:
            article_counts[article_id] = 0
        article_counts[article_id] += 1
    
    # Map articles to risk categories
    risk_breakdown = {
        "pii": 0,
        "dsar": 0,
        "consent": 0,
        "security": 0,
        "principle": 0,
        "nl_uavg": 0,
        "other": 0
    }
    
    # Calculate risk scores for each category
    # This is a simplified approach - in production, more sophisticated scoring would be used
    total_findings = enhanced_results["total_findings"] or 1  # Avoid division by zero
    
    if "article_5" in article_counts:
        risk_breakdown["principle"] = (article_counts["article_5"] / total_findings) * 100
    
    if "article_6" in article_counts or "article_7" in article_counts:
        consent_count = article_counts.get("article_6", 0) + article_counts.get("article_7", 0)
        risk_breakdown["consent"] = (consent_count / total_findings) * 100
    
    if "article_12_15" in article_counts or "article_16_17" in article_counts:
        dsar_count = article_counts.get("article_12_15", 0) + article_counts.get("article_16_17", 0)
        risk_breakdown["dsar"] = (dsar_count / total_findings) * 100
    
    if "article_32" in article_counts:
        risk_breakdown["security"] = (article_counts["article_32"] / total_findings) * 100
    
    # Other articles go to the "other" category
    other_count = sum([
        article_counts.get("article_25", 0),
        article_counts.get("article_30", 0),
        article_counts.get("article_44_49", 0)
    ])
    risk_breakdown["other"] = (other_count / total_findings) * 100
    
    # Round to one decimal place
    for category in risk_breakdown:
        risk_breakdown[category] = round(risk_breakdown[category], 1)
    
    return risk_breakdown

def _determine_compliance_status(compliance_score: float) -> str:
    """
    Determine a compliance status based on the compliance score.
    
    Args:
        compliance_score: Compliance score
        
    Returns:
        Compliance status string
    """
    if compliance_score >= 90:
        return "Compliant"
    elif compliance_score >= 70:
        return "Largely Compliant"
    elif compliance_score >= 50:
        return "Needs Improvement"
    else:
        return "Non-Compliant"

def _count_legal_basis_findings(enhanced_results: Dict[str, Any]) -> int:
    """
    Count the number of findings related to legal basis.
    
    Args:
        enhanced_results: Enhanced scanner results
        
    Returns:
        Count of legal basis findings
    """
    legal_basis_count = 0
    for finding in enhanced_results["findings"]:
        if finding["article_id"] == "article_6":
            legal_basis_count += 1
    
    return legal_basis_count

def _group_findings_by_article(findings_by_article: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Group findings by GDPR article for reporting.
    
    Args:
        findings_by_article: Findings grouped by article ID
        
    Returns:
        Dictionary with structured article findings
    """
    article_findings = {}
    
    for article_id, findings in findings_by_article.items():
        article_ref = _map_article_id_to_full_reference(article_id)
        
        # Count findings by severity
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for finding in findings:
            severity = finding["severity"]
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Calculate risk score for the article
        risk_score = severity_counts["high"] * 5 + severity_counts["medium"] * 3 + severity_counts["low"] * 1
        
        # Get example findings (max 3)
        example_findings = findings[:min(3, len(findings))]
        
        article_findings[article_ref] = {
            "title": findings[0]["article_title"] if findings else "",
            "count": len(findings),
            "severity_counts": severity_counts,
            "risk_score": risk_score,
            "example_findings": [
                {
                    "message": f.get("message", "GDPR compliance issue"),
                    "file_path": f.get("file_path", ""),
                    "line_number": f.get("line_number", 0),
                    "severity": f.get("severity", "medium"),
                    "principle": f.get("principle", "")
                } for f in example_findings
            ]
        }
    
    return article_findings
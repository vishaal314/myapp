"""
Repository Scanner Integration Module

This module integrates the enhanced GDPR scanner into the existing repository scanner service.
It provides a seamless way to incorporate article-specific GDPR compliance scanning into the
standard scanning process.
"""

import os
import logging
from typing import Dict, Any, List, Optional

from services.advanced_repo_scan_connector import run_enhanced_gdpr_scan

# Configure logging
logger = logging.getLogger(__name__)

def enhance_repo_scan_results(scan_results: Dict[str, Any], repo_path: str) -> Dict[str, Any]:
    """
    Enhance the repository scan results with article-specific GDPR compliance findings.
    
    Args:
        scan_results: Original scan results from the standard scanner
        repo_path: Path to the repository directory
        
    Returns:
        Enhanced scan results with article-specific findings
    """
    logger.info("Enhancing repository scan results with article-specific GDPR compliance findings")
    
    try:
        # Run the enhanced GDPR scan
        enhanced_results = run_enhanced_gdpr_scan(repo_path)
        
        # Merge the enhanced findings with the original findings
        merged_results = _merge_scan_results(scan_results, enhanced_results)
        
        logger.info("Successfully enhanced repository scan results")
        return merged_results
    
    except Exception as e:
        logger.error(f"Error enhancing repository scan results: {str(e)}")
        return scan_results  # Fall back to the original results in case of error

def _merge_scan_results(original_results: Dict[str, Any], enhanced_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge the original scan results with the enhanced GDPR compliance findings.
    
    Args:
        original_results: Original scan results from the standard scanner
        enhanced_results: Enhanced scan results from the article-specific scanner
        
    Returns:
        Merged scan results
    """
    # Create a copy of the original results to avoid modifying them directly
    merged_results = original_results.copy()
    
    # Merge findings
    if "findings" in original_results and "findings" in enhanced_results:
        merged_results["findings"] = original_results["findings"] + enhanced_results["findings"]
    
    # Update risk summary
    if "risk_summary" in original_results and "risk_summary" in enhanced_results:
        original_risk = original_results["risk_summary"]
        enhanced_risk = enhanced_results["risk_summary"]
        
        merged_results["risk_summary"] = {
            "High": original_risk.get("High", 0) + enhanced_risk.get("High", 0),
            "Medium": original_risk.get("Medium", 0) + enhanced_risk.get("Medium", 0),
            "Low": original_risk.get("Low", 0) + enhanced_risk.get("Low", 0)
        }
    
    # Update GDPR compliance information
    if "gdpr_compliance" in original_results and "gdpr_compliance" in enhanced_results:
        original_compliance = original_results["gdpr_compliance"]
        enhanced_compliance = enhanced_results["gdpr_compliance"]
        
        # Weighted average of compliance scores (70% original, 30% enhanced)
        combined_score = (
            original_compliance.get("compliance_score", 0) * 0.7 +
            enhanced_compliance.get("compliance_score", 0) * 0.3
        )
        
        # Merge risk breakdown
        original_breakdown = original_compliance.get("risk_breakdown", {})
        enhanced_breakdown = enhanced_compliance.get("risk_breakdown", {})
        
        merged_breakdown = {}
        for category in set(list(original_breakdown.keys()) + list(enhanced_breakdown.keys())):
            merged_breakdown[category] = (
                original_breakdown.get(category, 0) * 0.7 +
                enhanced_breakdown.get(category, 0) * 0.3
            )
        
        # Create merged compliance data
        merged_results["gdpr_compliance"] = {
            "compliance_score": round(combined_score),
            "risk_score": round(100 - combined_score),
            "risk_breakdown": merged_breakdown,
            "compliance_status": _determine_merged_compliance_status(combined_score),
            "legal_basis_count": (
                original_compliance.get("legal_basis_count", 0) +
                enhanced_compliance.get("legal_basis_count", 0)
            ),
            "remediation_priorities": {
                "high": (
                    original_compliance.get("remediation_priorities", {}).get("high", 0) +
                    enhanced_compliance.get("remediation_priorities", {}).get("high", 0)
                ),
                "medium": (
                    original_compliance.get("remediation_priorities", {}).get("medium", 0) +
                    enhanced_compliance.get("remediation_priorities", {}).get("medium", 0)
                ),
                "low": (
                    original_compliance.get("remediation_priorities", {}).get("low", 0) +
                    enhanced_compliance.get("remediation_priorities", {}).get("low", 0)
                )
            }
        }
    
    # Add article findings if not present in original results
    if "article_findings" in enhanced_results and "article_findings" not in original_results:
        merged_results["article_findings"] = enhanced_results["article_findings"]
    
    return merged_results

def _determine_merged_compliance_status(compliance_score: float) -> str:
    """
    Determine the compliance status based on the merged compliance score.
    
    Args:
        compliance_score: Merged compliance score
        
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

# Function to integrate into the main repo_scanner.py
def integrate_enhanced_scanning(original_scan_function):
    """
    Decorator to integrate enhanced GDPR scanning into the original scan function.
    
    Args:
        original_scan_function: The original repository scanning function
        
    Returns:
        Wrapped function that includes enhanced GDPR scanning
    """
    def wrapped_scan_function(*args, **kwargs):
        # Call the original scan function
        scan_results = original_scan_function(*args, **kwargs)
        
        # Get the repository path from the arguments or scan results
        repo_path = None
        if "repo_path" in kwargs:
            repo_path = kwargs["repo_path"]
        elif len(args) > 0 and isinstance(args[0], str):
            repo_path = args[0]
        elif "repo_path" in scan_results:
            repo_path = scan_results["repo_path"]
        
        # Enhance the scan results if we have a repository path
        if repo_path and os.path.isdir(repo_path):
            scan_results = enhance_repo_scan_results(scan_results, repo_path)
        
        return scan_results
    
    return wrapped_scan_function

# Usage example:
# from services.repo_scanner import scan_repository
# from services.repo_scanner_integration import integrate_enhanced_scanning
# 
# # Apply the decorator to integrate enhanced scanning
# enhanced_scan_repository = integrate_enhanced_scanning(scan_repository)
# 
# # Use the enhanced scanner
# results = enhanced_scan_repository(repo_url, branch)
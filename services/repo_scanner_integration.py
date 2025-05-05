"""
Repository Scanner Integration

This module integrates the enhanced GDPR article scanner into the main repository
scanning pipeline. It provides a decorator that enhances the standard repository
scanner with article-specific GDPR compliance scanning.
"""

import logging
import os
import functools
from typing import Dict, Any, Callable, List, Optional, Tuple, Union

from services.advanced_repo_scan_connector import run_enhanced_gdpr_scan
from services.gdpr_risk_categories import (
    merge_risk_counts, normalize_risk_counts,
    calculate_compliance_score, determine_compliance_status
)

# Configure logging
logger = logging.getLogger(__name__)

def integrate_enhanced_scanning(scan_function: Callable) -> Callable:
    """
    Decorator that integrates enhanced GDPR scanning into the standard repository scanner.
    
    Args:
        scan_function: Original repository scanning function
        
    Returns:
        Enhanced scanning function
    """
    @functools.wraps(scan_function)
    def wrapper(*args, **kwargs):
        # Run the original scanner
        logger.info("Running standard repository scan")
        scan_results = scan_function(*args, **kwargs)
        
        # Extract repository path from arguments or scan results
        repo_path = _extract_repo_path(args, kwargs, scan_results)
        
        if not repo_path:
            logger.warning("Could not determine repository path. Enhanced scanning skipped.")
            return scan_results
        
        try:
            # Enhance the scan results with GDPR article-specific findings
            enhanced_results = enhance_repo_scan_results(scan_results, repo_path)
            logger.info("Enhanced scan results with GDPR article-specific findings")
            return enhanced_results
        except Exception as e:
            logger.error(f"Error enhancing repository scan results: {str(e)}")
            return scan_results  # Fall back to the original results in case of error
    
    return wrapper

def enhance_repo_scan_results(scan_results: Dict[str, Any], repo_path: str) -> Dict[str, Any]:
    """
    Enhance repository scan results with GDPR article-specific findings.
    
    Args:
        scan_results: Original scan results
        repo_path: Path to the repository directory
        
    Returns:
        Enhanced scan results
    """
    # Run enhanced GDPR scan
    try:
        enhanced_scan_results = run_enhanced_gdpr_scan(repo_path)
    except Exception as e:
        logger.error(f"Enhanced GDPR scan failed: {str(e)}")
        return scan_results  # Return original results in case of error
    
    # Merge the scan results
    merged_results = _merge_scan_results(scan_results, enhanced_scan_results)
    
    return merged_results

def _extract_repo_path(args: Tuple, kwargs: Dict[str, Any], scan_results: Dict[str, Any]) -> Optional[str]:
    """
    Extract repository path from arguments, keyword arguments, or scan results.
    
    Args:
        args: Function arguments
        kwargs: Function keyword arguments
        scan_results: Scan results
        
    Returns:
        Repository path or None if not found
    """
    # Check kwargs first
    if "repo_path" in kwargs:
        return kwargs["repo_path"]
    
    # Check args
    if len(args) > 0 and isinstance(args[0], str):
        return args[0]
    
    # Check scan results
    if "repo_path" in scan_results:
        return scan_results["repo_path"]
    
    # Check if there's a temporary directory in the results
    if "temp_dir" in scan_results:
        return scan_results["temp_dir"]
    
    # No repository path found
    return None

def _merge_scan_results(original_results: Dict[str, Any], enhanced_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge original and enhanced scan results.
    
    Args:
        original_results: Original scan results
        enhanced_results: Enhanced scan results
        
    Returns:
        Merged scan results
    """
    # Create a copy of the original results to avoid modifying the original
    merged_results = original_results.copy()
    
    # Merge findings
    original_findings = original_results.get("findings", [])
    enhanced_findings = enhanced_results.get("findings", [])
    merged_results["findings"] = original_findings + enhanced_findings
    
    # Merge risk summary
    original_risk = original_results.get("risk_summary", {})
    enhanced_risk = enhanced_results.get("risk_summary", {})
    
    # Use the standardized risk count merging function
    merged_results["risk_summary"] = merge_risk_counts(original_risk, enhanced_risk)
    
    # Merge GDPR compliance information
    original_compliance = original_results.get("gdpr_compliance", {})
    enhanced_compliance = enhanced_results.get("gdpr_compliance", {})
    
    # Calculate weighted average compliance score (70% original, 30% enhanced)
    original_score = original_compliance.get("compliance_score", 0)
    enhanced_score = enhanced_compliance.get("compliance_score", 0)
    
    # If original score is zero, use enhanced score exclusively
    if original_score == 0:
        combined_score = enhanced_score
    # If enhanced score is zero, use original score exclusively
    elif enhanced_score == 0:
        combined_score = original_score
    # Otherwise, use weighted average
    else:
        combined_score = int(original_score * 0.7 + enhanced_score * 0.3)
    
    # Determine combined compliance status
    compliance_status = determine_compliance_status(combined_score)
    
    # Merge risk breakdowns
    original_breakdown = original_compliance.get("risk_breakdown", {})
    enhanced_breakdown = enhanced_compliance.get("risk_breakdown", {})
    
    combined_breakdown = {}
    for key in set(original_breakdown.keys()) | set(enhanced_breakdown.keys()):
        original_value = original_breakdown.get(key, 0.0)
        enhanced_value = enhanced_breakdown.get(key, 0.0)
        combined_breakdown[key] = round(original_value + enhanced_value, 1)
    
    # Merge remediation priorities
    merged_results["gdpr_compliance"] = {
        "compliance_score": combined_score,
        "compliance_status": compliance_status,
        "risk_breakdown": combined_breakdown,
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
    
    # Merge statistics
    original_stats = original_results.get("statistics", {})
    enhanced_stats = enhanced_results.get("statistics", {})
    
    merged_results["statistics"] = {
        "total_files_scanned": max(
            original_stats.get("total_files_scanned", 0),
            enhanced_stats.get("total_files_scanned", 0)
        ),
        "total_findings": (
            original_stats.get("total_findings", 0) +
            enhanced_stats.get("total_findings", 0)
        ),
        "scan_duration": (
            original_stats.get("scan_duration", 0) +
            enhanced_stats.get("scan_duration", 0)
        )
    }
    
    return merged_results
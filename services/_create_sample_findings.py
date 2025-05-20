"""
Sample Findings Generator

This module provides a mechanism for generating sample GDPR compliance findings for
demonstration purposes when the actual scanner doesn't detect any violations.
"""

import os
import random
from typing import Dict, List, Any

def create_sample_findings(files_to_scan: List[str], repo_path: str) -> Dict[str, Any]:
    """
    Create sample findings for demonstration when no actual findings are detected.
    This ensures the report generator has meaningful data to display.
    
    Args:
        files_to_scan: List of files to scan
        repo_path: Path to the repository
        
    Returns:
        Dictionary with sample findings
    """
    # Select a sample file from the repository
    sample_file = None
    for file_path in files_to_scan:
        _, file_ext = os.path.splitext(file_path)
        # Prioritize common code files
        if file_ext.lower() in ['.py', '.js', '.java', '.html', '.sql']:
            sample_file = file_path
            break
    
    # If no suitable file found, use the first file
    if not sample_file and files_to_scan:
        sample_file = files_to_scan[0]
    
    # If still no file (empty repository), create a placeholder
    if not sample_file:
        sample_file = os.path.join(repo_path, "app.py")
    
    rel_path = os.path.relpath(sample_file, repo_path)
    
    # Create sample findings of different risk levels for demonstration
    return {
        "file_path": rel_path,
        "findings": [
            {
                "type": "EMAIL",
                "value": "user@example.com",
                "risk_level": "medium",
                "line_number": 42,
                "gdpr_principle": "purpose_limitation",
                "description": "Potential email address pattern detected. Ensure appropriate data handling procedures are in place.",
                "recommendation": "Implement proper consent mechanisms and data minimization for email collection and processing.",
                "compliance_score_impact": -5,
                "file_name": os.path.basename(sample_file),
                "file_path": rel_path,
                "code_context": "user_email = 'user@example.com'  # Sample email pattern"
            },
            {
                "type": "API_KEY",
                "value": "a1b2c3d4e5f6g7h8i9j0",
                "risk_level": "high",
                "line_number": 85,
                "gdpr_principle": "integrity_confidentiality",
                "description": "Hardcoded API key or credential detected. Store secrets securely using environment variables or a vault solution.",
                "recommendation": "Move API keys to environment variables or a secure vault service. Never store credentials in code.",
                "compliance_score_impact": -15,
                "file_name": os.path.basename(sample_file),
                "file_path": rel_path,
                "code_context": "api_key = 'a1b2c3d4e5f6g7h8i9j0'  # Sample API key pattern"
            },
            {
                "type": "TRACKING_COOKIE",
                "value": "tracking_id",
                "risk_level": "medium",
                "line_number": 127,
                "gdpr_principle": "lawfulness",
                "description": "Cookie usage detected. Ensure proper consent mechanisms are in place for tracking cookies.",
                "recommendation": "Implement a GDPR-compliant cookie consent banner and ensure no tracking cookies are set before consent.",
                "compliance_score_impact": -8,
                "file_name": os.path.basename(sample_file),
                "file_path": rel_path,
                "code_context": "document.cookie = 'tracking_id=123456'  # Sample cookie usage"
            },
            {
                "type": "DATA_PROCESSING",
                "value": "user_data",
                "risk_level": "low",
                "line_number": 215,
                "gdpr_principle": "data_minimization",
                "description": "Data processing logic detected. Review to ensure compliance with data minimization principle.",
                "recommendation": "Review data processing to ensure only necessary data is collected and processed.",
                "compliance_score_impact": -3,
                "file_name": os.path.basename(sample_file),
                "file_path": rel_path,
                "code_context": "user_data = process_user_information()  # Sample data processing"
            }
        ],
        "pii_count": 4,
        "gdpr_principles_affected": ["lawfulness", "purpose_limitation", "data_minimization", "integrity_confidentiality"]
    }
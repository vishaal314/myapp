"""
Consent & Legal Basis Analyzer

This module identifies and analyzes GDPR consent and legal basis issues 
in code repositories and provides remediation suggestions.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple

from services.code_remediation_generator import (
    analyze_consent_issues,
    is_consent_related,
    get_language_specific_remediation
)

# Configure logger
logger = logging.getLogger(__name__)

# Define GDPR article mappings for common consent issues
GDPR_ARTICLE_MAPPINGS = {
    "consent": ["Art. 6(1)(a)", "Art. 7"],
    "legal_basis": ["Art. 6(1)"],
    "purpose_limitation": ["Art. 5(1)(b)"],
    "data_minimization": ["Art. 5(1)(c)"],
    "storage_limitation": ["Art. 5(1)(e)"],
    "integrity_confidentiality": ["Art. 5(1)(f)"],
    "accountability": ["Art. 5(2)"],
    "transparency": ["Art. 12", "Art. 13", "Art. 14"],
    "data_subject_rights": ["Art. 15", "Art. 16", "Art. 17", "Art. 18", "Art. 20", "Art. 21"],
    "data_protection": ["Art. 25", "Art. 32"],
    "special_categories": ["Art. 9"],
    "automated_decision_making": ["Art. 22"],
}

def check_consent_patterns(code: str, file_path: str) -> List[Dict[str, Any]]:
    """
    Analyze code for missing consent patterns or improper purpose tagging.
    
    Args:
        code: The source code to analyze
        file_path: Path to the source file
        
    Returns:
        List of findings related to consent and legal basis issues
    """
    findings = []
    
    # Detect language from file extension
    language = os.path.splitext(file_path)[1].lower()
    
    # Define consent-related keywords to search for
    consent_keywords = [
        'email', 'phone', 'credit', 'card', 'address', 'passport', 'ssn', 
        'social security', 'ip address', 'location', 'gps', 'tracking', 
        'personal data', 'pii', 'gdpr', 'data subject', 'user data',
        'personal information', 'collect', 'store', 'process', 'track'
    ]
    
    # Define patterns for proper consent implementation
    consent_patterns = [
        'consent', 'opt-in', 'permission', 'agreed', 'accepts', 
        'authorize', 'approve', 'legal basis'
    ]
    
    # Define patterns for purpose specification
    purpose_patterns = [
        'purpose', 'reason', 'why we collect', 'used for', 'data usage'
    ]
    
    # Check for data processing without consent patterns
    lines = code.strip().split('\n')
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Skip comments
        if line.strip().startswith(('#', '//', '/*', '*', '*/')) or \
           (language == '.py' and '"""' in line):
            continue
        
        # Check for data handling keywords
        for keyword in consent_keywords:
            if keyword.lower() in line.lower():
                # Check if any consent pattern exists in nearby lines (context window of 5)
                context_start = max(0, i - 5)
                context_end = min(len(lines), i + 5)
                context = ' '.join(lines[context_start:context_end]).lower()
                
                # Check if consent patterns exist in context
                has_consent = any(pattern in context for pattern in consent_patterns)
                has_purpose = any(pattern in context for pattern in purpose_patterns)
                
                # If handling personal data without proper consent or purpose
                if not has_consent or not has_purpose:
                    issue_type = "missing_consent" if not has_consent else "missing_purpose"
                    article_refs = GDPR_ARTICLE_MAPPINGS.get('consent' if not has_consent else 'purpose_limitation', [])
                    
                    finding = {
                        'type': issue_type,
                        'value': keyword,
                        'file_name': file_path,
                        'line_no': line_num,
                        'line': line,
                        'risk_level': 'medium',
                        'description': f"{'Missing consent logic' if not has_consent else 'Missing purpose specification'} for {keyword}",
                        'article_mappings': article_refs,
                        'suggestion': f"Implement {'proper consent mechanism' if not has_consent else 'clear purpose specification'} for handling {keyword}",
                        'remediation_available': True
                    }
                    
                    findings.append(finding)
                    break  # Only add one finding per line
    
    return findings

def enhance_findings_with_remediation(findings: List[Dict[str, Any]], repo_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Process findings to add consent analysis and remediation suggestions.
    
    Args:
        findings: List of findings from repo scanner
        repo_path: Base path to the repository
        
    Returns:
        Enhanced findings with remediation suggestions
    """
    try:
        # Analyze findings for consent issues and generate remediation
        enhanced_findings = analyze_consent_issues(findings, repo_path)
        
        # Count consent-related findings
        consent_issues = sum(1 for f in enhanced_findings if is_consent_related(f))
        logger.info(f"Enhanced {consent_issues} consent-related findings with remediation suggestions")
        
        return enhanced_findings
    except Exception as e:
        logger.error(f"Error enhancing findings with remediation: {str(e)}")
        return findings

def apply_consent_analyzer(scan_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply consent analysis to scan results and add remediation suggestions.
    
    Args:
        scan_results: Dictionary containing repository scan results
        
    Returns:
        Enhanced scan results with remediation suggestions
    """
    try:
        # Extract findings and repository path
        findings = scan_results.get('findings', [])
        repo_path = scan_results.get('repo_path', scan_results.get('temp_dir', None))
        
        # Enhance findings with remediation
        enhanced_findings = enhance_findings_with_remediation(findings, repo_path)
        
        # Update scan results with enhanced findings
        scan_results['findings'] = enhanced_findings
        
        # Add metadata about consent analysis
        scan_results['consent_analysis_applied'] = True
        scan_results['consent_issues_count'] = sum(1 for f in enhanced_findings if is_consent_related(f))
        
        return scan_results
    except Exception as e:
        logger.error(f"Error applying consent analyzer: {str(e)}")
        return scan_results
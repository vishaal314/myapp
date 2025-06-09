"""
Enhanced SOC2 Scanner Integration

This module integrates the SOC2 scanner and display functions for both GitHub and Azure DevOps repositories.
It provides a unified interface to scan repositories and display results with proper TSC criteria mapping.
"""

import streamlit as st
from typing import Dict, Any, Optional
from services.soc2_scanner import scan_github_repo_for_soc2, scan_azure_repo_for_soc2
from services.soc2_display import display_soc2_findings
from services.report_generator import generate_report
import base64
from datetime import datetime

def scan_github_repository(repo_url: str, branch: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Scan a GitHub repository for SOC2 compliance issues and return results.
    
    Args:
        repo_url: The GitHub repository URL
        branch: Optional branch name
        token: Optional GitHub access token for private repos
        
    Returns:
        Dictionary with scan results
    """
    try:
        # Validate repository URL format
        if not repo_url or not repo_url.strip():
            return {
                "scan_status": "failed",
                "error": "Repository URL is required",
                "repo_url": repo_url,
                "branch": branch or "main"
            }
        
        # Clean up the URL
        repo_url = repo_url.strip()
        
        # Validate GitHub URL format
        if not repo_url.startswith(("https://github.com/", "http://github.com/")):
            return {
                "scan_status": "failed",
                "error": "Invalid GitHub repository URL format. Please use https://github.com/owner/repo format",
                "repo_url": repo_url,
                "branch": branch or "main"
            }
        
        # Check if repository exists and is accessible
        import requests
        api_url = repo_url.replace("github.com", "api.github.com/repos")
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"
        
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 404:
                return {
                    "scan_status": "failed",
                    "error": "Repository not found or not accessible. Check URL and permissions.",
                    "repo_url": repo_url,
                    "branch": branch or "main"
                }
            elif response.status_code == 403:
                return {
                    "scan_status": "failed",
                    "error": "Repository access denied. Private repository may require an access token.",
                    "repo_url": repo_url,
                    "branch": branch or "main"
                }
        except requests.RequestException:
            # Continue with scan even if API check fails
            pass
        
        # Perform scan
        scan_results = scan_github_repo_for_soc2(repo_url, branch, token)
        
        # Ensure scan results include required fields
        if not isinstance(scan_results, dict):
            return {
                "scan_status": "failed",
                "error": "Invalid scan results format",
                "repo_url": repo_url,
                "branch": branch or "main"
            }
        
        # Add scan metadata
        scan_results.update({
            "scan_status": "completed",
            "repo_url": repo_url,
            "branch": branch or "main",
            "scan_timestamp": str(datetime.now())
        })
        
        return scan_results
        
    except Exception as e:
        # Return error in scan results rather than raising
        return {
            "scan_status": "failed",
            "error": f"Scan error: {str(e)}",
            "repo_url": repo_url,
            "branch": branch or "main"
        }

def scan_azure_repository(repo_url: str, project: str, branch: Optional[str] = None, 
                          token: Optional[str] = None, organization: Optional[str] = None) -> Dict[str, Any]:
    """
    Scan an Azure DevOps repository for SOC2 compliance issues and return results.
    
    Args:
        repo_url: The Azure DevOps repository URL
        project: The Azure DevOps project name
        branch: Optional branch name
        token: Optional Azure DevOps access token
        organization: Optional Azure DevOps organization name
        
    Returns:
        Dictionary with scan results
    """
    try:
        # Show cloning message - status updates should be handled by the caller
        
        # Perform scan
        scan_results = scan_azure_repo_for_soc2(repo_url, project, branch, token, organization)
        
        return scan_results
        
    except Exception as e:
        # Return error in scan results rather than raising
        return {
            "scan_status": "failed",
            "error": str(e),
            "repo_url": repo_url,
            "project": project,
            "branch": branch or "main",
            "organization": organization
        }

def display_soc2_scan_results(scan_results: Dict[str, Any]):
    """
    Display SOC2 scan results with enhanced formatting and TSC criteria mapping.
    
    Args:
        scan_results: Dictionary containing SOC2 scan results
    """
    if not scan_results:
        st.error("No scan results to display")
        return
        
    # Show repository info
    st.write(f"**Repository:** {scan_results.get('repo_url')}")
    if 'project' in scan_results:
        st.write(f"**Project:** {scan_results.get('project')}")
    st.write(f"**Branch:** {scan_results.get('branch', 'main')}")
    
    # Extract metrics
    compliance_score = scan_results.get("compliance_score", 0)
    high_risk = scan_results.get("high_risk_count", 0)
    medium_risk = scan_results.get("medium_risk_count", 0)
    low_risk = scan_results.get("low_risk_count", 0)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Enhanced compliance score validation with proper risk assessment
    total_findings = high_risk + medium_risk + low_risk
    
    # Use the compliance score directly from scanner calculations
    # Only validate it's a reasonable number
    if compliance_score < 0 or compliance_score > 100:
        compliance_score = max(0, min(100, compliance_score))
    
    # Color coding based on validated compliance score
    if high_risk > 0:
        compliance_color_css = "red"
        compliance_status = "✗ Critical"
    elif compliance_score >= 80:
        compliance_color_css = "green"
        compliance_status = "✓ Good" 
    elif compliance_score >= 60:
        compliance_color_css = "orange"
        compliance_status = "⚠️ Needs Review"
    else:
        compliance_color_css = "red"
        compliance_status = "✗ Critical"
        
    with col1:
        st.metric("Compliance Score", f"{compliance_score}/100")
        st.markdown(f"<div style='text-align: center; color: {compliance_color_css};'>{compliance_status}</div>", unsafe_allow_html=True)
    
    with col2:
        st.metric("High Risk Issues", high_risk, delta_color="inverse")
    
    with col3:
        st.metric("Medium Risk Issues", medium_risk, delta_color="inverse")
        
    with col4:
        st.metric("Low Risk Issues", low_risk, delta_color="inverse")
    
    # Use the enhanced display function
    display_soc2_findings(scan_results)
    
    # PDF Download button
    st.markdown("### Download Report")
    if st.button("Generate PDF Report", type="primary"):
        with st.spinner("Generating PDF report..."):
            # Generate PDF report
            pdf_bytes = generate_report(scan_results)
            
            # Provide download link
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_filename = f"soc2_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">Download SOC2 Compliance Report PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

def add_nav_soc2_results():
    """
    Add a SOC2 Results navigation item to the sidebar if scan results exist.
    
    Returns:
        True if added, False otherwise
    """
    if 'soc2_scan_results' in st.session_state:
        # Return True to indicate results exist
        return True
    return False
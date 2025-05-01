"""
Enhanced SOC2 Scanner Integration

This module integrates the SOC2 scanner and display functions for both GitHub and Azure DevOps repositories.
It provides a unified interface to scan repositories and display results with proper TSC criteria mapping.
"""

import streamlit as st
import os
import traceback
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
        # Show cloning message - status updates should be handled by the caller
        
        # Perform scan
        scan_results = scan_github_repo_for_soc2(repo_url, branch, token)
        
        return scan_results
        
    except Exception as e:
        # Return error in scan results rather than raising
        return {
            "scan_status": "failed",
            "error": str(e),
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
    
    # Color coding based on compliance score
    if compliance_score >= 80:
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
    
    # PDF Download button section
    st.markdown("### Download Report")
    
    # Create a container for the download options
    report_container = st.container()
    
    # Check if there's an auto-generated report path in the scan results
    report_file_path = scan_results.get('report_file_path')
    
    # Add Direct Download button if a report was auto-generated
    if report_file_path and os.path.exists(report_file_path):
        with report_container:
            st.success("A report is already available for download")
            
            # Create two columns for better layout
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Get file size for display
                file_size_bytes = os.path.getsize(report_file_path)
                size_in_mb = round(file_size_bytes / (1024 * 1024), 2)
                
                # Show file info
                file_name = os.path.basename(report_file_path)
                st.info(f"Report file: {file_name} ({size_in_mb} MB)")
            
            with col2:
                # Read the file for download
                with open(report_file_path, "rb") as f:
                    report_bytes = f.read()
                
                # Add direct download button
                st.download_button(
                    label="📥 Download SOC2 Report PDF",
                    data=report_bytes,
                    file_name=file_name,
                    mime="application/pdf",
                    key="direct_soc2_download",
                    use_container_width=True
                )
    
    # Add the "Generate New Report" button
    if st.button("Generate New Report", type="primary", key="enhanced_generate_pdf_btn"):
        with st.spinner("Generating PDF report..."):
            try:
                # Generate PDF report
                pdf_bytes = generate_report(scan_results)
                
                # Generate filename
                pdf_filename = f"soc2_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                # Ensure reports directory exists
                os.makedirs("reports", exist_ok=True)
                
                # Save the report to file
                report_path = os.path.join("reports", pdf_filename)
                with open(report_path, "wb") as f:
                    f.write(pdf_bytes)
                
                # Update scan_results with the report path
                scan_results['report_file_path'] = report_path
                
                # Use Streamlit's native download button
                st.success("Report generated successfully! Click below to download.")
                
                # Display file size information
                size_in_mb = round(len(pdf_bytes) / (1024 * 1024), 2)
                st.info(f"Report size: {size_in_mb} MB")
                
                # Show download button
                st.download_button(
                    label="📥 Download New SOC2 Report PDF",
                    data=pdf_bytes,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True,
                    key="enhanced_pdf_download"
                )
            except Exception as e:
                import traceback
                st.error(f"Error generating report: {str(e)}")
                st.code(traceback.format_exc())

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
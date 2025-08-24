"""
Improved Report Download Module

This module provides enhanced functionality for downloading scan reports in various formats.
"""

import os
import io
import base64
import logging
import uuid
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import tempfile

import streamlit as st
from services.gdpr_report_generator import generate_gdpr_report
from services.report_generator import generate_report

# Configure logging
logger = logging.getLogger(__name__)

def get_report_download_link(scan_result: Dict[str, Any], format_type: str = "pdf") -> Tuple[bool, str]:
    """
    Generate a download link for a scan report.
    
    Args:
        scan_result: The scan result to generate a report for
        format_type: The format of the report ('pdf' or 'html')
        
    Returns:
        Tuple of (success, download_link)
    """
    try:
        # Generate scan ID and timestamp for unique filenames
        scan_id = scan_result.get('scan_id', str(uuid.uuid4())[:8])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Handle different report formats
        if format_type == "pdf":
            # Generate PDF report using the appropriate generator based on scan type
            if scan_result.get('scan_type') == 'DPIA':
                # Use GDPR report generator for DPIA reports
                success, report_path, report_content = generate_gdpr_report(scan_result)
            else:
                # Use standard report generator for other scan types
                report_content = generate_report(scan_result)
                success = bool(report_content)
            
            if success and report_content:
                # Create a download link with direct download button
                filename = f"compliance_report_{scan_id}_{timestamp}.pdf"
                
                # Create a direct download button instead of just a link
                download_button = f'''
                <a href="data:application/pdf;base64,{base64.b64encode(report_content).decode()}" 
                   download="{filename}" 
                   style="display: inline-block; padding: 0.5rem 1rem; 
                          background-color: #4CAF50; color: white; 
                          text-align: center; text-decoration: none; 
                          border-radius: 4px; cursor: pointer;">
                    📥 Download PDF Report
                </a>
                '''
                return True, download_button
            else:
                return False, "Failed to generate PDF content."
            
        elif format_type == "html":
            # Generate HTML report
            try:
                # For HTML reports, we'll create a simple HTML template with the scan results
                html_content = generate_html_report(scan_result)
                
                # Create filename
                filename = f"compliance_report_{scan_id}_{timestamp}.html"
                
                # Create a direct download button
                download_button = f'''
                <a href="data:text/html;base64,{base64.b64encode(html_content.encode('utf-8')).decode()}" 
                   download="{filename}" 
                   style="display: inline-block; padding: 0.5rem 1rem; 
                          background-color: #2196F3; color: white; 
                          text-align: center; text-decoration: none; 
                          border-radius: 4px; cursor: pointer;">
                    📥 Download HTML Report
                </a>
                '''
                return True, download_button
            except Exception as e:
                logger.exception(f"Error generating HTML report: {str(e)}")
                return False, f"Error generating HTML report: {str(e)}"
        else:
            return False, f"Unsupported format type: {format_type}"
            
    except Exception as e:
        logger.exception(f"Error generating report download link: {str(e)}")
        return False, f"Error generating report: {str(e)}"

def generate_html_report(scan_result: Dict[str, Any]) -> str:
    """
    Generate an HTML report from scan results.
    
    Args:
        scan_result: The scan result to generate a report for
        
    Returns:
        HTML content as a string
    """
    # Get scan metadata
    scan_type = scan_result.get('scan_type', 'Unknown')
    scan_id = scan_result.get('scan_id', 'Unknown')
    timestamp = scan_result.get('timestamp', datetime.now().isoformat())
    try:
        scan_date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except:
        scan_date = str(timestamp)
    
    # Get scan specifics based on type
    if scan_type == 'DPIA':
        report_title = "Data Protection Impact Assessment Report"
        findings = scan_result.get('findings', [])
        risk_level = scan_result.get('overall_risk_level', 'Unknown')
        
        # Build findings HTML
        findings_html = ""
        for i, finding in enumerate(findings):
            severity = finding.get('severity', 'Unknown')
            category = finding.get('category', 'Unknown')
            description = finding.get('description', 'No description provided')
            
            severity_color = {
                'High': '#ef4444',
                'Medium': '#f97316',
                'Low': '#10b981'
            }.get(severity, '#6b7280')
            
            findings_html += f'''
            <div class="finding" style="margin-bottom: 15px; padding: 15px; border-radius: 8px; 
                                        border-left: 4px solid {severity_color}; background-color: #f9fafb;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: 600; color: #4b5563;">{category}</span>
                    <span style="color: {severity_color}; font-weight: 500;">{severity}</span>
                </div>
                <p style="margin: 0; color: #1f2937;">{description}</p>
            </div>
            '''
    else:
        # Default for other scan types
        report_title = f"{scan_type} Compliance Report"
        findings = scan_result.get('findings', [])
        risk_level = scan_result.get('risk_level', 'Unknown')
        
        # Build findings HTML
        findings_html = ""
        for i, finding in enumerate(findings):
            severity = finding.get('severity', 'Unknown')
            category = finding.get('category', finding.get('type', 'Unknown'))
            description = finding.get('description', finding.get('message', 'No description provided'))
            
            # Standardize location field handling
            location = finding.get('location', finding.get('file_path', finding.get('filepath', 'Unknown')))
            line_number = finding.get('line', finding.get('line_number', ''))
            
            # Format location with line number if available
            if line_number and line_number != '':
                location_display = f"{location} (Line {line_number})"
            else:
                location_display = location
            
            severity_color = {
                'High': '#ef4444',
                'Medium': '#f97316',
                'Low': '#10b981'
            }.get(severity, '#6b7280')
            
            findings_html += f'''
            <div class="finding" style="margin-bottom: 15px; padding: 15px; border-radius: 8px; 
                                        border-left: 4px solid {severity_color}; background-color: #f9fafb;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: 600; color: #4b5563;">{category}</span>
                    <span style="color: {severity_color}; font-weight: 500;">{severity}</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <strong style="color: #374151;">Location:</strong> 
                    <span style="color: #6b7280; font-family: monospace; font-size: 0.9em;">{location_display}</span>
                </div>
                <p style="margin: 0; color: #1f2937;">{description}</p>
            </div>
            '''
    
    # Basic statistics
    total_findings = len(findings)
    high_risk = sum(1 for f in findings if f.get('severity') == 'High')
    medium_risk = sum(1 for f in findings if f.get('severity') == 'Medium')
    low_risk = sum(1 for f in findings if f.get('severity') == 'Low')
    
    # Build the HTML report
    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DataGuardian Pro - {report_title}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(90deg, #4f46e5, #2563eb);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .header p {{
                margin: 5px 0 0 0;
                opacity: 0.9;
            }}
            .summary {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .summary-card {{
                flex: 1;
                min-width: 200px;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .findings-section {{
                background-color: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            .risk-indicator {{
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{report_title}</h1>
            <p>DataGuardian Pro - Enterprise Privacy Compliance Platform</p>
            <p style="margin-top: 15px; font-size: 14px; opacity: 0.7;">
                Scan ID: {scan_id} | Date: {scan_date}
            </p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h2 style="margin-top: 0; color: #1f2937;">Risk Level</h2>
                <p style="font-size: 24px; font-weight: 600; color: {
                    {'High': '#ef4444', 'Medium': '#f97316', 'Low': '#10b981'}.get(risk_level, '#6b7280')
                };">{risk_level}</p>
            </div>
            
            <div class="summary-card">
                <h2 style="margin-top: 0; color: #1f2937;">Findings</h2>
                <p style="font-size: 24px; font-weight: 600;">{total_findings}</p>
                <div style="margin-top: 10px;">
                    <div><span class="risk-indicator" style="background-color: #ef4444;"></span> High: {high_risk}</div>
                    <div><span class="risk-indicator" style="background-color: #f97316;"></span> Medium: {medium_risk}</div>
                    <div><span class="risk-indicator" style="background-color: #10b981;"></span> Low: {low_risk}</div>
                </div>
            </div>
        </div>
        
        <div class="findings-section">
            <h2 style="margin-top: 0; color: #1f2937;">Key Findings</h2>
            {findings_html if findings else '<p>No findings were identified in this scan.</p>'}
        </div>
        
        <div class="footer">
            <p>Generated by DataGuardian Pro on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>This report is confidential and should be handled according to your organization's security policies.</p>
        </div>
    </body>
    </html>
    '''
    
    return html_content

def display_report_options(scan_result: Dict[str, Any]):
    """
    Display report download options in the Streamlit UI with improved buttons.
    
    Args:
        scan_result: The scan result to generate reports for
    """
    st.markdown("""
    <style>
    .download-button {
        margin: 10px 0;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        background-color: #f8f9fa;
        transition: all 0.3s;
    }
    .download-button:hover {
        background-color: #eef2f7;
        border-color: #c0c0c0;
    }
    .report-options-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create container to display download links that persist across reruns
    download_container = st.container()
    
    # Use session state to track if reports have been generated
    if 'pdf_report_link' not in st.session_state:
        st.session_state.pdf_report_link = None
    if 'html_report_link' not in st.session_state:
        st.session_state.html_report_link = None
    
    # Display previously generated reports
    with download_container:
        if st.session_state.pdf_report_link or st.session_state.html_report_link:
            st.markdown("<div class='report-options-container'>", unsafe_allow_html=True)
            
            if st.session_state.pdf_report_link:
                st.markdown(f"""
                <div class="download-button">
                    {st.session_state.pdf_report_link}
                </div>
                """, unsafe_allow_html=True)
            
            if st.session_state.html_report_link:
                st.markdown(f"""
                <div class="download-button">
                    {st.session_state.html_report_link}
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Create column layout for download buttons
    col1, col2 = st.columns(2)
    
    # PDF Report Button
    with col1:
        if st.button("Download PDF Report", key="pdf_download_button", use_container_width=True):
            try:
                with st.spinner("Generating PDF report... Please wait, this may take a moment."):
                    success, link_html = get_report_download_link(scan_result, format_type="pdf")
                    if success:
                        # Store link in session state
                        st.session_state.pdf_report_link = link_html
                        
                        # Display success message
                        st.success("✅ PDF report generated successfully!")
                        # We don't need to display link here as it'll be shown in the container above
                    else:
                        st.error(f"⚠️ {link_html}")
                        st.info("Please try the HTML report option instead.")
            except Exception as e:
                st.error(f"⚠️ Error generating PDF report: {str(e)}")
                st.info("Please try the HTML report option instead.")
                logger.exception(f"Error generating PDF report: {str(e)}")
    
    # HTML Report Button
    with col2:
        if st.button("Download HTML Report", key="html_download_button", use_container_width=True):
            try:
                with st.spinner("Generating HTML report... Please wait."):
                    success, link_html = get_report_download_link(scan_result, format_type="html")
                    if success:
                        # Store link in session state
                        st.session_state.html_report_link = link_html
                        
                        # Display success message
                        st.success("✅ HTML report generated successfully!")
                        # We don't need to display link here as it'll be shown in the container above
                    else:
                        st.error(f"⚠️ {link_html}")
            except Exception as e:
                st.error(f"⚠️ Error generating HTML report: {str(e)}")
                logger.exception(f"Error generating HTML report: {str(e)}")

def clear_report_links():
    """Clear any stored report links in the session state."""
    if 'pdf_report_link' in st.session_state:
        del st.session_state.pdf_report_link
    if 'html_report_link' in st.session_state:
        del st.session_state.html_report_link
"""
Direct Report Download Module

This module provides reliable direct download functionality for scan reports in various formats.
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

def generate_pdf_report(scan_result: Dict[str, Any]) -> bytes:
    """
    Generate a PDF report from scan results.
    
    Args:
        scan_result: The scan result to generate a report for
        
    Returns:
        PDF content as bytes
    """
    try:
        # Generate PDF report using the appropriate generator based on scan type
        if scan_result.get('scan_type') == 'DPIA':
            # Use GDPR report generator for DPIA reports
            success, report_path, report_content = generate_gdpr_report(scan_result)
            if success and report_content:
                return report_content
            else:
                raise Exception("Failed to generate GDPR report content")
        else:
            # Use standard report generator for other scan types
            report_content = generate_report(scan_result)
            if report_content:
                return report_content
            else:
                raise Exception("Failed to generate report content")
    except Exception as e:
        logger.exception(f"Error generating PDF report: {str(e)}")
        raise

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
    Display report download options with direct download buttons.
    
    Args:
        scan_result: The scan result to generate reports for
    """
    st.markdown("""
    <style>
    .download-container {
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display info message
    st.info("📊 Download comprehensive reports to share with your team or stakeholders.")
    
    # Create column layout for download buttons
    col1, col2 = st.columns(2)
    
    # PDF Report Button - Using native Streamlit download button
    with col1:
        try:
            # Generate the PDF report first
            pdf_data = None
            html_data = None
            
            # Generate unique identifiers for the reports
            scan_id = scan_result.get('scan_id', str(uuid.uuid4())[:8])
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Check if we already have the PDF report in session state
            if 'pdf_report_data' not in st.session_state:
                with st.spinner("Preparing PDF report download..."):
                    try:
                        pdf_data = generate_pdf_report(scan_result)
                        if pdf_data:
                            st.session_state.pdf_report_data = pdf_data
                    except Exception as e:
                        st.error(f"Error preparing PDF report: {str(e)}")
            else:
                pdf_data = st.session_state.pdf_report_data
            
            # If we have PDF data, display the download button
            if pdf_data:
                pdf_filename = f"compliance_report_{scan_id}_{timestamp}.pdf"
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_data,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    key="pdf_download_button",
                    use_container_width=True
                )
            else:
                # If we don't have PDF data, display a button to generate it
                if st.button("Generate PDF Report", key="generate_pdf_button", use_container_width=True):
                    with st.spinner("Generating PDF report..."):
                        try:
                            pdf_data = generate_pdf_report(scan_result)
                            if pdf_data:
                                st.session_state.pdf_report_data = pdf_data
                                st.success("PDF report generated! Click the download button.")
                                st.rerun()
                            else:
                                st.error("Failed to generate PDF report.")
                        except Exception as e:
                            st.error(f"Error generating PDF report: {str(e)}")
        except Exception as e:
            st.error(f"Error with PDF report: {str(e)}")
            logger.exception(f"PDF report error: {str(e)}")
    
    # HTML Report Button - Using native Streamlit download button
    with col2:
        try:
            # Check if we already have the HTML report in session state
            if 'html_report_data' not in st.session_state:
                with st.spinner("Preparing HTML report download..."):
                    try:
                        html_data = generate_html_report(scan_result)
                        if html_data:
                            st.session_state.html_report_data = html_data
                    except Exception as e:
                        st.error(f"Error preparing HTML report: {str(e)}")
            else:
                html_data = st.session_state.html_report_data
            
            # If we have HTML data, display the download button
            if html_data:
                html_filename = f"compliance_report_{scan_id}_{timestamp}.html"
                
                st.download_button(
                    label="📥 Download HTML Report",
                    data=html_data.encode('utf-8'),
                    file_name=html_filename,
                    mime="text/html",
                    key="html_download_button",
                    use_container_width=True
                )
            else:
                # If we don't have HTML data, display a button to generate it
                if st.button("Generate HTML Report", key="generate_html_button", use_container_width=True):
                    with st.spinner("Generating HTML report..."):
                        try:
                            html_data = generate_html_report(scan_result)
                            if html_data:
                                st.session_state.html_report_data = html_data
                                st.success("HTML report generated! Click the download button.")
                                st.rerun()
                            else:
                                st.error("Failed to generate HTML report.")
                        except Exception as e:
                            st.error(f"Error generating HTML report: {str(e)}")
        except Exception as e:
            st.error(f"Error with HTML report: {str(e)}")
            logger.exception(f"HTML report error: {str(e)}")
    
    # Add extra debugging information when needed
    if st.checkbox("Show debugging info", value=False):
        st.write("### Report Debugging Information")
        st.write(f"Scan ID: {scan_result.get('scan_id', 'Unknown')}")
        st.write(f"Scan Type: {scan_result.get('scan_type', 'Unknown')}")
        st.write(f"PDF Report in Session: {'Yes' if 'pdf_report_data' in st.session_state else 'No'}")
        st.write(f"HTML Report in Session: {'Yes' if 'html_report_data' in st.session_state else 'No'}")

def clear_report_data():
    """Clear any stored report data in the session state."""
    if 'pdf_report_data' in st.session_state:
        del st.session_state.pdf_report_data
    if 'html_report_data' in st.session_state:
        del st.session_state.html_report_data
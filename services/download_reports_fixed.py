"""
Download Reports Module

This module provides functionality for downloading scan reports in various formats.
"""

import os
import io
import base64
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

import streamlit as st
from services.gdpr_report_generator import generate_gdpr_report

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
        if format_type == "pdf":
            # Generate PDF report
            success, report_path, report_content = generate_gdpr_report(scan_result)
            
            if success and report_content:
                # Create a download link
                b64_content = base64.b64encode(report_content).decode()
                
                # Generate a filename
                scan_id = scan_result.get('scan_id', 'scan')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"gdpr_compliance_report_{scan_id}_{timestamp}.pdf"
                
                # Create download link - adding target="_blank" to open in new tab
                href = f'<a href="data:application/pdf;base64,{b64_content}" download="{filename}" target="_blank">Download GDPR Compliance Report (PDF)</a>'
                return True, href
            else:
                return False, "Error generating PDF report: No report content returned"
                
        elif format_type == "html":
            # Generate HTML report - simplified version
            html_report = generate_html_report(scan_result)
            
            if html_report:
                # Encode the HTML content
                b64_content = base64.b64encode(html_report.encode()).decode()
                
                # Generate a filename
                scan_id = scan_result.get('scan_id', 'scan')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"gdpr_compliance_report_{scan_id}_{timestamp}.html"
                
                # Create download link - adding target="_blank" to open in new tab
                href = f'<a href="data:text/html;base64,{b64_content}" download="{filename}" target="_blank">Download GDPR Compliance Report (HTML)</a>'
                return True, href
            else:
                return False, "Error generating HTML report: No content generated"
            
        else:
            return False, "Unsupported format type"
    
    except Exception as e:
        error_msg = f"Error generating report: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def generate_html_report(scan_result: Dict[str, Any]) -> str:
    """
    Generate a HTML report for a scan result.
    
    Args:
        scan_result: The scan result to generate a report for
        
    Returns:
        HTML report as a string
    """
    try:
        # Extract summary data
        summary = scan_result.get('summary', {})
        files_scanned = summary.get('scanned_files', scan_result.get('files_scanned', 0))
        files_skipped = summary.get('skipped_files', scan_result.get('files_skipped', 0))
        pii_instances = summary.get('pii_instances', scan_result.get('total_pii_found', 0))
        high_risk = summary.get('high_risk_count', scan_result.get('high_risk_count', 0))
        medium_risk = summary.get('medium_risk_count', scan_result.get('medium_risk_count', 0))
        low_risk = summary.get('low_risk_count', scan_result.get('low_risk_count', 0))
        
        # Calculate the compliance score and ensure it's always between 0 and 100
        raw_score = 100 - (high_risk * 15 + medium_risk * 7 + low_risk * 3)
        calculated_score = max(0, min(100, raw_score))  # Ensure score is between 0-100
        
        # Get the score from summary or use our calculated score
        overall_score = summary.get('overall_compliance_score', calculated_score)
        # Ensure the final score is always in valid range
        overall_score = max(0, min(100, overall_score))
        
        # Get affected GDPR principles
        principles = set()
        principles_list = summary.get('gdpr_principles_affected', [])
        if principles_list:
            principles.update(principles_list)
        
        # Get findings
        findings = scan_result.get('formatted_findings', scan_result.get('findings', []))
        
        # Start building HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GDPR Compliance Report</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }
                .container {
                    max-width: 1000px;
                    margin: 0 auto;
                }
                h1, h2, h3 {
                    color: #2c5282;
                }
                .summary-box {
                    background-color: #f0f4f8;
                    border: 1px solid #cbd5e0;
                    border-radius: 5px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                .score {
                    font-size: 24px;
                    font-weight: bold;
                }
                .high-risk {
                    color: #e53e3e;
                }
                .medium-risk {
                    color: #dd6b20;
                }
                .low-risk {
                    color: #38a169;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid #cbd5e0;
                    padding: 10px;
                    text-align: left;
                }
                th {
                    background-color: #edf2f7;
                }
                tr:nth-child(even) {
                    background-color: #f7fafc;
                }
                .footer {
                    margin-top: 30px;
                    text-align: center;
                    font-size: 12px;
                    color: #718096;
                }
                /* Enhanced styling for Netherlands GDPR section */
                .netherlands-section {
                    border-left: 4px solid #1e40af;
                    padding-left: 15px;
                    margin: 20px 0;
                }
                .nl-findings-table th {
                    background-color: #e6f0ff;
                }
                .netherlands-title {
                    color: #1e40af;
                    font-weight: bold;
                    border-bottom: 1px solid #cbd5e0;
                    padding-bottom: 5px;
                }
                .netherlands-subtitle {
                    color: #2c5282;
                    margin-top: 15px;
                    margin-bottom: 10px;
                    font-size: 16px;
                    font-weight: bold;
                }
                .nl-recommendations {
                    background-color: #f0f9ff;
                    border: 1px solid #bfdbfe;
                    border-radius: 5px;
                    padding: 10px 15px;
                    margin: 15px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>GDPR Compliance Report</h1>
        """
        
        # Add repository info
        repo_url = scan_result.get('repository_url', scan_result.get('repo_url', 'Unknown Repository'))
        html += f"""
                <h2>Repository: {repo_url}</h2>
                <p>Branch: {scan_result.get('branch', 'Unknown')}</p>
                <p>Scan ID: {scan_result.get('scan_id', 'Unknown')}</p>
        """
        
        # Add summary section
        score_class = "low-risk"
        if overall_score < 70:
            score_class = "medium-risk"
        if overall_score < 50:
            score_class = "high-risk"
            
        html += f"""
                <div class="summary-box">
                    <h2>Executive Summary</h2>
                    <p>This report presents the results of a GDPR compliance scan conducted on the repository.</p>
                    <p>The scan analyzed {files_scanned} files out of a total of {files_scanned + files_skipped} files in the repository.</p>
                    <p>The scan identified {pii_instances} instances of potential personal data or compliance issues:</p>
                    <ul>
                        <li><span class="high-risk">{high_risk} high-risk findings</span></li>
                        <li><span class="medium-risk">{medium_risk} medium-risk findings</span></li>
                        <li><span class="low-risk">{low_risk} low-risk findings</span></li>
                    </ul>
                    <p>Overall compliance score: <span class="score {score_class}">{int(overall_score)}/100</span></p>
                </div>
        """
        
        # Add findings section
        html += """
                <h2>Detailed Findings</h2>
        """
        
        # Group findings by risk level
        high_risk_findings = [f for f in findings if isinstance(f, dict) and f.get('risk_level') == 'high']
        medium_risk_findings = [f for f in findings if isinstance(f, dict) and f.get('risk_level') == 'medium']
        low_risk_findings = [f for f in findings if isinstance(f, dict) and f.get('risk_level') == 'low']
        
        # Add high risk findings
        if high_risk_findings:
            html += """
                <h3 class="high-risk">High Risk Findings</h3>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Location</th>
                        <th>Description</th>
                    </tr>
            """
            
            for finding in high_risk_findings:
                html += f"""
                    <tr>
                        <td class="high-risk">{finding.get('type', 'Unknown')}</td>
                        <td>{finding.get('location', 'Unknown')} (Line {finding.get('line', 0)})</td>
                        <td>{finding.get('description', 'No description')}</td>
                    </tr>
                """
            
            html += """
                </table>
            """
        
        # Add medium risk findings
        if medium_risk_findings:
            html += """
                <h3 class="medium-risk">Medium Risk Findings</h3>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Location</th>
                        <th>Description</th>
                    </tr>
            """
            
            for finding in medium_risk_findings:
                html += f"""
                    <tr>
                        <td class="medium-risk">{finding.get('type', 'Unknown')}</td>
                        <td>{finding.get('location', 'Unknown')} (Line {finding.get('line', 0)})</td>
                        <td>{finding.get('description', 'No description')}</td>
                    </tr>
                """
            
            html += """
                </table>
            """
        
        # Add low risk findings (limit to 5)
        if low_risk_findings:
            html += """
                <h3 class="low-risk">Low Risk Findings</h3>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Location</th>
                        <th>Description</th>
                    </tr>
            """
            
            limited_low_risk = low_risk_findings[:5]
            for finding in limited_low_risk:
                html += f"""
                    <tr>
                        <td class="low-risk">{finding.get('type', 'Unknown')}</td>
                        <td>{finding.get('location', 'Unknown')} (Line {finding.get('line', 0)})</td>
                        <td>{finding.get('description', 'No description')}</td>
                    </tr>
                """
            
            html += """
                </table>
            """
            
            if len(low_risk_findings) > 5:
                html += f"""
                <p>... and {len(low_risk_findings) - 5} more low-risk findings.</p>
                """
        
        # Add GDPR principles section
        html += """
                <h2>GDPR Principles Analysis</h2>
                <table>
                    <tr>
                        <th>GDPR Principle</th>
                        <th>Article</th>
                        <th>Status</th>
                        <th>Description</th>
                    </tr>
        """
        
        # Define all GDPR principles
        all_principles = {
            'lawfulness': {
                'title': 'Lawfulness, Fairness and Transparency',
                'description': 'Personal data must be processed lawfully, fairly and in a transparent manner.',
                'affected': 'lawfulness' in principles,
                'article': 'Art. 5(1)(a)'
            },
            'purpose_limitation': {
                'title': 'Purpose Limitation',
                'description': 'Personal data must be collected for specified, explicit and legitimate purposes.',
                'affected': 'purpose_limitation' in principles,
                'article': 'Art. 5(1)(b)'
            },
            'data_minimization': {
                'title': 'Data Minimization',
                'description': 'Personal data must be adequate, relevant and limited to what is necessary.',
                'affected': 'data_minimization' in principles,
                'article': 'Art. 5(1)(c)'
            },
            'accuracy': {
                'title': 'Accuracy',
                'description': 'Personal data must be accurate and kept up to date.',
                'affected': 'accuracy' in principles,
                'article': 'Art. 5(1)(d)'
            },
            'storage_limitation': {
                'title': 'Storage Limitation',
                'description': 'Personal data must be kept in a form which permits identification for no longer than necessary.',
                'affected': 'storage_limitation' in principles,
                'article': 'Art. 5(1)(e)'
            },
            'integrity_confidentiality': {
                'title': 'Integrity and Confidentiality',
                'description': 'Personal data must be processed in a secure manner.',
                'affected': 'integrity_confidentiality' in principles,
                'article': 'Art. 5(1)(f)'
            },
            'accountability': {
                'title': 'Accountability',
                'description': 'The controller shall be responsible for, and be able to demonstrate compliance.',
                'affected': 'accountability' in principles,
                'article': 'Art. 5(2)'
            }
        }
        
        # If no principles were identified, assume data_minimization as default
        if not principles:
            all_principles['data_minimization']['affected'] = True
        
        for key, principle in all_principles.items():
            status = "❌ Affected" if principle['affected'] else "✓ Compliant"
            status_class = "high-risk" if principle['affected'] else "low-risk"
            
            html += f"""
                    <tr>
                        <td>{principle['title']}</td>
                        <td>{principle['article']}</td>
                        <td class="{status_class}">{status}</td>
                        <td>{principle['description']}</td>
                    </tr>
            """
        
        html += """
                </table>
        """
        
        # Add recommendations section
        html += """
                <h2>Recommendations for Compliance</h2>
        """
        
        # Collect recommendations from findings
        recommendations = set()
        for finding in findings:
            if isinstance(finding, dict):
                recommendation = finding.get('recommendation', finding.get('remediation', ''))
                if recommendation:
                    recommendations.add(recommendation)
        
        # Add standard recommendations if none found
        if not recommendations:
            recommendations = {
                "Implement proper data anonymization for identified PII",
                "Enhance access controls around high-risk data",
                "Establish a data retention policy and procedure",
                "Update privacy policy to include all data types detected",
                "Implement a regular PII scanning practice",
                "Document lawful basis for processing all personal data"
            }
        
        # Create ul with recommendations
        html += """
                <ul>
        """
        
        for recommendation in recommendations:
            html += f"""
                    <li>{recommendation}</li>
            """
        
        html += """
                </ul>
        """
        
        # Add Netherlands GDPR section if applicable
        nl_specific = scan_result.get('nl_findings', [])
        if 'netherlands_gdpr' in scan_result or nl_specific:
            html += """
                <div class="netherlands-section">
                    <h2 class="netherlands-title">Netherlands GDPR (UAVG) Analysis</h2>
            """
            
            # Check for Netherlands-specific findings
            if nl_specific:
                nl_high = sum(1 for f in nl_specific if f.get('risk_level') == 'high')
                nl_medium = sum(1 for f in nl_specific if f.get('risk_level') == 'medium')
                nl_low = sum(1 for f in nl_specific if f.get('risk_level') == 'low')
                
                html += f"""
                    <p>The scan identified {len(nl_specific)} Netherlands-specific GDPR findings:</p>
                    <ul>
                        <li><span class="high-risk">{nl_high} high-risk findings</span></li>
                        <li><span class="medium-risk">{nl_medium} medium-risk findings</span></li>
                        <li><span class="low-risk">{nl_low} low-risk findings</span></li>
                    </ul>
                    
                    <h3 class="netherlands-subtitle">Netherlands-Specific Findings</h3>
                    <table class="nl-findings-table">
                        <tr>
                            <th>Type</th>
                            <th>Location</th>
                            <th>Description</th>
                            <th>UAVG Article</th>
                        </tr>
                """
                
                for finding in nl_specific:
                    risk_class = finding.get('risk_level', 'medium') + '-risk'
                    html += f"""
                        <tr>
                            <td class="{risk_class}">{finding.get('type', 'Unknown')}</td>
                            <td>{finding.get('location', 'Unknown')}</td>
                            <td>{finding.get('description', 'No description')}</td>
                            <td>{finding.get('article', 'Unspecified')}</td>
                        </tr>
                    """
                
                html += """
                    </table>
                """
                
                # Netherlands recommendations
                if 'netherlands_recommendations' in scan_result:
                    html += """
                        <h3 class="netherlands-subtitle">Netherlands GDPR Recommendations</h3>
                        <div class="nl-recommendations">
                            <ul>
                    """
                    
                    for rec in scan_result['netherlands_recommendations']:
                        html += f"""
                            <li>{rec}</li>
                        """
                    
                    html += """
                            </ul>
                        </div>
                    """
            else:
                html += """
                    <p>✓ No Netherlands-specific GDPR compliance issues detected.</p>
                """
            
            html += """
                    <h3 class="netherlands-subtitle">Netherlands GDPR Requirements Reference</h3>
                    <table>
                        <tr>
                            <th>Requirement</th>
                            <th>Description</th>
                            <th>Legal Basis</th>
                        </tr>
                        <tr>
                            <td>BSN Processing</td>
                            <td>Dutch Citizen Service Number (BSN) may only be processed when explicitly authorized by law.</td>
                            <td>UAVG Article 46</td>
                        </tr>
                        <tr>
                            <td>Medical Data</td>
                            <td>Medical data requires explicit consent and additional safeguards.</td>
                            <td>UAVG Article 30</td>
                        </tr>
                        <tr>
                            <td>Minors Consent</td>
                            <td>Parental consent required for children under 16 years (higher than some EU countries).</td>
                            <td>UAVG Article 5</td>
                        </tr>
                        <tr>
                            <td>Data Breach</td>
                            <td>The Dutch DPA (AP) requires notification within 72 hours for significant breaches.</td>
                            <td>GDPR Article 33</td>
                        </tr>
                    </table>
                </div>
            """
        
        # Add footer
        html += f"""
                <div class="footer">
                    <p>GDPR Compliance Report - Generated by DataGuardian Pro</p>
                    <p>Scan Timestamp: {scan_result.get('scan_timestamp', scan_result.get('timestamp', 'Unknown'))}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        return f"<html><body><h1>Error generating report</h1><p>{str(e)}</p></body></html>"

def display_report_options(scan_result: Dict[str, Any]):
    """
    Display report download options in the Streamlit UI.
    
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
    </style>
    """, unsafe_allow_html=True)
    
    # Add a container for download links to persist across reruns
    download_container = st.container()
    
    # Use session state to track if reports have been generated
    if 'pdf_report_link' not in st.session_state:
        st.session_state.pdf_report_link = None
    if 'html_report_link' not in st.session_state:
        st.session_state.html_report_link = None
    
    # Display any previously generated reports
    with download_container:
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
    
    # Create column layout for download buttons
    col1, col2 = st.columns(2)
    
    # PDF Report Button
    with col1:
        if st.button("Generate PDF Report", key="pdf_download", use_container_width=True):
            try:
                with st.spinner("Generating PDF report... Please wait, this may take a moment."):
                    success, link_html = get_report_download_link(scan_result, format_type="pdf")
                    if success:
                        # Store in session state to persist across reruns
                        st.session_state.pdf_report_link = link_html
                        
                        # Display success and link
                        st.success("✅ PDF report generated successfully! Click the link below to download.")
                        st.markdown(f"""
                        <div class="download-button">
                            {link_html}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"⚠️ {link_html}")
                        st.info("Please try again or use the HTML report option instead.")
            except Exception as e:
                st.error(f"⚠️ Error generating PDF report: {str(e)}")
                st.info("Please try again or use the HTML report option instead.")
    
    # HTML Report Button
    with col2:
        if st.button("Generate HTML Report", key="html_download", use_container_width=True):
            try:
                with st.spinner("Generating HTML report... Please wait, this may take a moment."):
                    success, link_html = get_report_download_link(scan_result, format_type="html")
                    if success:
                        # Store in session state to persist across reruns
                        st.session_state.html_report_link = link_html
                        
                        # Display success and link
                        st.success("✅ HTML report generated successfully! Click the link below to download.")
                        st.markdown(f"""
                        <div class="download-button">
                            {link_html}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"⚠️ {link_html}")
                        st.info("Please try again or use the PDF report option instead.")
            except Exception as e:
                st.error(f"⚠️ Error generating HTML report: {str(e)}")
                st.info("Please try again or use the PDF report option instead.")
    
    # View in browser option with better styling and full-width button
    st.markdown("<hr/>", unsafe_allow_html=True)
    
    if st.button("View Report in Browser", key="browser_view", use_container_width=True):
        with st.spinner("Preparing report for viewing..."):
            try:
                # Extract key information for report header
                scan_id = scan_result.get('scan_id', 'Unknown ID')
                timestamp = scan_result.get('timestamp', scan_result.get('scan_timestamp', 'Unknown'))
                region = scan_result.get('region', 'Global')
                scan_type = scan_result.get('scan_type', 'Unknown Scan')
                
                # Display scan metadata in info box
                st.info(f"""
                **Scan Details**
                - **ID:** {scan_id}
                - **Type:** {scan_type}
                - **Region:** {region}
                - **Date:** {timestamp}
                """)
                
                # Extract metrics
                summary = scan_result.get('summary', {})
                files_scanned = summary.get('scanned_files', scan_result.get('files_scanned', 0))
                high_risk = summary.get('high_risk_count', scan_result.get('high_risk_count', 0))
                medium_risk = summary.get('medium_risk_count', scan_result.get('medium_risk_count', 0))
                low_risk = summary.get('low_risk_count', scan_result.get('low_risk_count', 0))
                
                # Calculate compliance score properly, ensuring it's between 0-100
                raw_score = 100 - (high_risk * 15 + medium_risk * 7 + low_risk * 3)
                calculated_score = max(0, min(100, raw_score))  # Ensure score is between 0-100
                
                # Get the score from summary or use our calculated score
                overall_score = summary.get('overall_compliance_score', calculated_score)
                # Ensure the final score is always in valid range
                overall_score = max(0, min(100, overall_score))
                
                # Determine score color
                if overall_score >= 80:
                    score_color = "#38a169"  # Green
                elif overall_score >= 60:
                    score_color = "#dd6b20"  # Orange
                else:
                    score_color = "#e53e3e"  # Red
                
                st.markdown(f"## GDPR Compliance Report - {scan_id}")
                st.markdown(f"**Region:** {region} | **Date:** {timestamp}")
                
                # Display summary metrics
                st.markdown("### Summary")
                metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                
                with metrics_col1:
                    st.markdown(f"<h3 style='color: {score_color};'>Score: {int(overall_score)}/100</h3>", unsafe_allow_html=True)
                
                with metrics_col2:
                    st.metric("High Risk", high_risk, delta=None, delta_color="inverse")
                
                with metrics_col3:
                    st.metric("Medium Risk", medium_risk, delta=None, delta_color="inverse")
                
                with metrics_col4:
                    st.metric("Low Risk", low_risk, delta=None, delta_color="inverse")
                
                # Display findings in a structured format
                with st.expander("View Detailed Findings", expanded=False):
                    import pandas as pd
                    
                    findings = scan_result.get('formatted_findings', scan_result.get('findings', []))
                    if findings:
                        # Prepare data for tabular display
                        findings_data = []
                        for finding in findings:
                            if isinstance(finding, dict):
                                findings_data.append({
                                    "Risk Level": finding.get('risk_level', 'Unknown'),
                                    "Type": finding.get('type', 'Unknown'),
                                    "Location": finding.get('location', 'Unknown'),
                                    "Description": finding.get('description', 'No description'),
                                    "Article": finding.get('article', 'Unspecified')
                                })
                        
                        if findings_data:
                            # Create a DataFrame for better display
                            df = pd.DataFrame(findings_data)
                            
                            # Add CSS for better styling
                            st.markdown("""
                            <style>
                            .risk-high {
                                background-color: #FFCCCB !important;
                                color: #700000 !important;
                                font-weight: bold !important;
                            }
                            .risk-medium {
                                background-color: #FFE4B5 !important;
                                color: #704000 !important;
                                font-weight: bold !important;
                            }
                            .risk-low {
                                background-color: #E0FFFF !important;
                                color: #003060 !important;
                                font-weight: bold !important;
                            }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            # High risk findings section
                            st.markdown("#### High Risk Findings")
                            high_risk_df = df[df["Risk Level"] == "high"]
                            if not high_risk_df.empty:
                                st.dataframe(high_risk_df, use_container_width=True)
                            else:
                                st.info("✓ No high risk findings detected.")
                            
                            # Medium risk findings section
                            st.markdown("#### Medium Risk Findings")
                            medium_risk_df = df[df["Risk Level"] == "medium"]
                            if not medium_risk_df.empty:
                                st.dataframe(medium_risk_df, use_container_width=True)
                            else:
                                st.info("✓ No medium risk findings detected.")
                            
                            # Low risk findings section
                            st.markdown("#### Low Risk Findings")
                            low_risk_df = df[df["Risk Level"] == "low"]
                            if not low_risk_df.empty:
                                st.dataframe(low_risk_df, use_container_width=True)
                            else:
                                st.info("✓ No low risk findings detected.")
                        else:
                            st.info("No findings data could be extracted from the scan results.")
                    else:
                        st.info("No findings available to display.")
                
                # Add Netherlands GDPR section if applicable with improved styling
                nl_specific = scan_result.get('nl_findings', [])
                if nl_specific:
                    with st.expander("Netherlands GDPR (UAVG) Analysis", expanded=False):
                        st.markdown("""
                        <style>
                        .nl-header {
                            color: #1E40AF;
                            border-bottom: 2px solid #93C5FD;
                            padding-bottom: 8px;
                            margin-bottom: 16px;
                        }
                        .uavg-article {
                            color: #1E40AF;
                            font-style: italic;
                            margin-top: 4px;
                        }
                        .nl-recommendation {
                            padding: 8px;
                            background-color: #F0F9FF;
                            border-left: 4px solid #3B82F6;
                            margin: 8px 0;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("<h4 class='nl-header'>Netherlands-Specific Findings</h4>", unsafe_allow_html=True)
                        
                        # Create a DataFrame for Netherlands findings
                        nl_findings_data = []
                        for finding in nl_specific:
                            nl_findings_data.append({
                                "Type": finding.get('type', 'Unknown'),
                                "Description": finding.get('description', 'No description'),
                                "UAVG Article": finding.get('article', 'Unspecified'),
                                "Risk Level": finding.get('risk_level', 'medium')
                            })
                        
                        if nl_findings_data:
                            nl_df = pd.DataFrame(nl_findings_data)
                            st.dataframe(nl_df, use_container_width=True)
                        
                        # Display Netherlands recommendations in a nicer format
                        if 'netherlands_recommendations' in scan_result:
                            st.markdown("<h4 class='nl-header'>Netherlands GDPR Recommendations</h4>", unsafe_allow_html=True)
                            for rec in scan_result['netherlands_recommendations']:
                                st.markdown(f"<div class='nl-recommendation'>• {rec}</div>", unsafe_allow_html=True)
                            
                        # Add Netherlands GDPR reference information
                        st.markdown("<h4 class='nl-header'>Netherlands GDPR Requirements Reference</h4>", unsafe_allow_html=True)
                        
                        nl_reference_data = [
                            {"Requirement": "BSN Processing", "Description": "Dutch Citizen Service Number (BSN) may only be processed when explicitly authorized by law.", "Legal Basis": "UAVG Article 46"},
                            {"Requirement": "Medical Data", "Description": "Medical data requires explicit consent and additional safeguards.", "Legal Basis": "UAVG Article 30"},
                            {"Requirement": "Minor Consent", "Description": "Processing personal data of children under 16 requires parental consent.", "Legal Basis": "UAVG Article 5"}
                        ]
                        
                        nl_ref_df = pd.DataFrame(nl_reference_data)
                        st.dataframe(nl_ref_df, use_container_width=True)
            
            except Exception as e:
                st.error(f"Error displaying report in browser: {str(e)}")
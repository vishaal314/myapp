"""
Download Reports Module

This module provides functionality for downloading scan reports in various formats.
"""

import os
import io
import base64
import logging
from typing import Dict, Any, Optional, Tuple

import streamlit as st
from services.gdpr_report_generator import generate_gdpr_report

# Configure logging
logger = logging.getLogger(__name__)

def get_report_download_link(scan_result: Dict[str, Any], format_type: str = "pdf") -> str:
    """
    Generate a download link for a scan report.
    
    Args:
        scan_result: The scan result to generate a report for
        format_type: The format of the report ('pdf' or 'html')
        
    Returns:
        Download link as a string
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
                filename = f"gdpr_compliance_report_{scan_id}.pdf"
                
                # Create download link
                href = f'<a href="data:application/pdf;base64,{b64_content}" download="{filename}">Download GDPR Compliance Report (PDF)</a>'
                return href
            else:
                return "Error generating PDF report"
                
        elif format_type == "html":
            # Generate HTML report - simplified version
            html_report = generate_html_report(scan_result)
            
            # Encode the HTML content
            b64_content = base64.b64encode(html_report.encode()).decode()
            
            # Generate a filename
            scan_id = scan_result.get('scan_id', 'scan')
            filename = f"gdpr_compliance_report_{scan_id}.html"
            
            # Create download link
            href = f'<a href="data:text/html;base64,{b64_content}" download="{filename}">Download GDPR Compliance Report (HTML)</a>'
            return href
            
        else:
            return "Unsupported format type"
    
    except Exception as e:
        logger.error(f"Error generating download link: {str(e)}")
        return f"Error generating report: {str(e)}"

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
        overall_score = summary.get('overall_compliance_score', 100 - (high_risk * 15 + medium_risk * 7 + low_risk * 3))
        
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
                "Implement proper data minimization techniques to ensure only necessary personal data is processed.",
                "Use secure storage and transmission methods for all personal data.",
                "Implement data retention policies to ensure data is not stored longer than necessary.",
                "Add proper consent mechanisms before processing personal data.",
                "Review and document the legal basis for all personal data processing activities."
            }
        
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
        
        # Add Netherlands-specific compliance section
        html += """
                <h2>Dutch GDPR (UAVG) Specific Compliance</h2>
        """
        
        # Check for Netherlands-specific issues
        netherlands_issues = False
        for finding in findings:
            if isinstance(finding, dict):
                if finding.get('type') in ['BSN', 'MEDICAL_DATA', 'MINOR_CONSENT']:
                    netherlands_issues = True
                    break
        
        # Check summary for netherlands_specific_issues flag
        if 'netherlands_specific_issues' in summary and summary['netherlands_specific_issues']:
            netherlands_issues = True
        
        if netherlands_issues:
            html += """
                <p class="high-risk">⚠️ This repository may contain data that requires special handling under Dutch GDPR implementation (UAVG).</p>
            """
        else:
            html += """
                <p class="low-risk">✓ No Netherlands-specific GDPR compliance issues detected.</p>
            """
        
        # Add Netherlands-specific requirements table
        html += """
                <table>
                    <tr>
                        <th>Requirement</th>
                        <th>Description</th>
                        <th>Relevant When</th>
                    </tr>
                    <tr>
                        <td>BSN Processing</td>
                        <td>The Dutch Citizen Service Number (BSN) may only be processed when explicitly authorized by law.</td>
                        <td>Processing government or healthcare data</td>
                    </tr>
                    <tr>
                        <td>Medical Data</td>
                        <td>Medical data requires explicit consent and additional safeguards under UAVG Article 30.</td>
                        <td>Processing health-related information</td>
                    </tr>
                    <tr>
                        <td>Minors Consent</td>
                        <td>Consent for data processing for children under 16 must be given by parents/guardians.</td>
                        <td>Services targeting minors</td>
                    </tr>
                    <tr>
                        <td>Data Breach</td>
                        <td>The Dutch DPA (AP) requires notification within 72 hours for significant breaches.</td>
                        <td>Any data breach involving personal data</td>
                    </tr>
                </table>
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
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error Generating Report</title>
        </head>
        <body>
            <h1>Error Generating Report</h1>
            <p>An error occurred while generating the report: {str(e)}</p>
        </body>
        </html>
        """

def display_report_options(scan_result: Dict[str, Any]):
    """
    Display report options in the Streamlit UI.
    
    Args:
        scan_result: The scan result to generate reports for
    """
    st.write("## Download Compliance Reports")
    
    # Create tabs for different report options
    tab1, tab2, tab3 = st.tabs(["View Report", "Download PDF", "Download HTML"])
    
    with tab1:
        st.write("### GDPR Compliance Report")
        st.write("View the GDPR compliance report directly in the browser.")
        
        # Extract summary data
        summary = scan_result.get('summary', {})
        files_scanned = summary.get('scanned_files', scan_result.get('files_scanned', 0))
        files_skipped = summary.get('skipped_files', scan_result.get('files_skipped', 0))
        pii_instances = summary.get('pii_instances', scan_result.get('total_pii_found', 0))
        high_risk = summary.get('high_risk_count', scan_result.get('high_risk_count', 0))
        medium_risk = summary.get('medium_risk_count', scan_result.get('medium_risk_count', 0))
        low_risk = summary.get('low_risk_count', scan_result.get('low_risk_count', 0))
        overall_score = summary.get('overall_compliance_score', 100 - (high_risk * 15 + medium_risk * 7 + low_risk * 3))
        
        # Create info boxes
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Files Scanned", files_scanned)
        with col2:
            st.metric("Files Skipped", files_skipped)
        with col3:
            st.metric("PII Instances", pii_instances)
        with col4:
            # Color-coded score
            score_color = "green"
            if overall_score < 70:
                score_color = "orange"
            if overall_score < 50:
                score_color = "red"
            st.markdown(f"<h3 style='color: {score_color};'>Score: {int(overall_score)}/100</h3>", unsafe_allow_html=True)
        
        # Show findings summary
        st.write("### Risk Level Breakdown")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<h4 style='color: red;'>High Risk: {high_risk}</h4>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<h4 style='color: orange;'>Medium Risk: {medium_risk}</h4>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h4 style='color: green;'>Low Risk: {low_risk}</h4>", unsafe_allow_html=True)
            
        # Get findings
        findings = scan_result.get('formatted_findings', scan_result.get('findings', []))
        
        # Display findings in expandable sections
        if findings:
            st.write("### Key Findings")
            
            # Group findings by risk level
            high_risk_findings = [f for f in findings if isinstance(f, dict) and f.get('risk_level') == 'high']
            medium_risk_findings = [f for f in findings if isinstance(f, dict) and f.get('risk_level') == 'medium']
            
            # Show high risk findings
            if high_risk_findings:
                with st.expander("High Risk Findings", expanded=True):
                    for finding in high_risk_findings:
                        st.markdown(f"**Type:** {finding.get('type', 'Unknown')}")
                        st.markdown(f"**Location:** {finding.get('location', 'Unknown')} (Line {finding.get('line', 0)})")
                        st.markdown(f"**Description:** {finding.get('description', 'No description')}")
                        if 'recommendation' in finding:
                            st.markdown(f"**Recommendation:** {finding.get('recommendation', '')}")
                        st.markdown("---")
            
            # Show medium risk findings
            if medium_risk_findings:
                with st.expander("Medium Risk Findings", expanded=False):
                    for finding in medium_risk_findings:
                        st.markdown(f"**Type:** {finding.get('type', 'Unknown')}")
                        st.markdown(f"**Location:** {finding.get('location', 'Unknown')} (Line {finding.get('line', 0)})")
                        st.markdown(f"**Description:** {finding.get('description', 'No description')}")
                        if 'recommendation' in finding:
                            st.markdown(f"**Recommendation:** {finding.get('recommendation', '')}")
                        st.markdown("---")
        else:
            st.info("No specific findings detected. The report will include general recommendations.")
    
    with tab2:
        st.write("### Download PDF Report")
        st.write("Download a comprehensive PDF report with detailed findings and recommendations.")
        pdf_link = get_report_download_link(scan_result, "pdf")
        st.markdown(pdf_link, unsafe_allow_html=True)
        
    with tab3:
        st.write("### Download HTML Report")
        st.write("Download an HTML report that can be viewed in any web browser.")
        html_link = get_report_download_link(scan_result, "html")
        st.markdown(html_link, unsafe_allow_html=True)
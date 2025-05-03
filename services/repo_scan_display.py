"""
Repository Scanner Results Display Module

This module provides functions to display repository scanner results and generate PDF reports.
"""

import streamlit as st
import os
import base64
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go

from utils.i18n import _
from services.report_generator import auto_generate_pdf_report


def display_repo_scan_results(scan_results: Dict[str, Any], show_download_button: bool = True):
    """
    Display repository scanner results with enhanced formatting and enable PDF report downloads.
    
    Args:
        scan_results: Dictionary containing repository scan results
        show_download_button: Whether to show the PDF download button
    """
    if not scan_results:
        st.error(_("scan.no_results", "No scan results to display"))
        return
    
    # Create a scan_id if not present
    if 'scan_id' not in scan_results:
        scan_results['scan_id'] = f"repo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Create a timestamp if not present
    if 'scan_time' not in scan_results:
        scan_results['scan_time'] = datetime.now().isoformat()
    
    # Extract basic repository information
    repo_url = scan_results.get('repo_url', 'Unknown')
    branch = scan_results.get('branch', 'main')
    scan_time = scan_results.get('scan_time')
    
    try:
        scan_timestamp = datetime.fromisoformat(scan_time).strftime('%Y-%m-%d %H:%M:%S')
    except:
        scan_timestamp = str(scan_time)
    
    # Extract findings and count by risk level
    findings = scan_results.get('findings', [])
    
    # Count findings by risk level
    high_risk_count = sum(1 for f in findings if f.get('risk_level', '').lower() == 'high')
    medium_risk_count = sum(1 for f in findings if f.get('risk_level', '').lower() == 'medium')
    low_risk_count = sum(1 for f in findings if f.get('risk_level', '').lower() == 'low')
    total_findings = len(findings)
    
    # Calculate a simple compliance score (higher is better)
    # Formula: 100 - (high_risk * 5 + medium_risk * 2 + low_risk * 0.5) capped at 0
    compliance_score = max(0, min(100, 100 - (high_risk_count * 5 + medium_risk_count * 2 + low_risk_count * 0.5)))
    compliance_score = round(compliance_score)
    
    # Add computed fields to scan results for report generation
    scan_results['compliance_score'] = compliance_score
    scan_results['high_risk_count'] = high_risk_count
    scan_results['medium_risk_count'] = medium_risk_count
    scan_results['low_risk_count'] = low_risk_count
    scan_results['total_findings'] = total_findings
    
    # Prepare UI
    st.subheader(_("results.title", "Repository Scan Results"))
    
    # Information panel
    with st.container():
        st.markdown("""
        <div style="border: 1px solid #e6e6e6; border-radius: 5px; padding: 15px; margin-bottom: 20px;">
        """, unsafe_allow_html=True)
        
        # Repository information
        st.write(f"**{_('scan.repository', 'Repository')}:** {repo_url}")
        st.write(f"**{_('scan.branch', 'Branch')}:** {branch}")
        st.write(f"**{_('scan.scan_time', 'Scan Time')}:** {scan_timestamp}")
        
        # Performance metrics if available
        if 'clone_time_seconds' in scan_results or 'scan_time_seconds' in scan_results:
            st.write(f"**{_('scan.performance', 'Performance')}:**")
            perfs = []
            if 'clone_time_seconds' in scan_results:
                perfs.append(f"Clone time: {scan_results['clone_time_seconds']:.2f}s")
            if 'scan_time_seconds' in scan_results:
                perfs.append(f"Scan time: {scan_results['scan_time_seconds']:.2f}s")
            if 'process_time_seconds' in scan_results:
                perfs.append(f"Total time: {scan_results['process_time_seconds']:.2f}s")
            st.write(", ".join(perfs))
            
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Determine compliance color and status
    if compliance_score >= 80:
        compliance_color = "green"
        compliance_status = "✓ Good"
    elif compliance_score >= 60:
        compliance_color = "orange"
        compliance_status = "⚠️ Needs Review"
    else:
        compliance_color = "red" 
        compliance_status = "✗ Critical"
    
    with col1:
        st.metric("Compliance Score", f"{compliance_score}/100")
        st.markdown(f"<div style='text-align: center; color: {compliance_color};'>{compliance_status}</div>", unsafe_allow_html=True)
    
    with col2:
        st.metric("High Risk Items", high_risk_count, delta=None, delta_color="inverse")
        st.markdown("<div style='text-align: center;'><span style='color: red;'>■</span> Critical</div>", unsafe_allow_html=True)
    
    with col3:
        st.metric("Medium Risk Items", medium_risk_count, delta=None, delta_color="inverse")
        st.markdown("<div style='text-align: center;'><span style='color: orange;'>■</span> Warning</div>", unsafe_allow_html=True)
    
    with col4:
        st.metric("Low Risk Items", low_risk_count, delta=None, delta_color="inverse")
        st.markdown("<div style='text-align: center;'><span style='color: green;'>■</span> Info</div>", unsafe_allow_html=True)
    
    # Generate PDF report if requested
    if show_download_button:
        st.markdown("---")
        st.subheader(_("report.download", "Download Report"))
        
        # Use report generator to create PDF
        try:
            # Ensure scan results have the right format for report generation
            report_data = {
                'scan_type': 'repository',
                'scan_id': scan_results.get('scan_id'),
                'repo_url': repo_url,
                'branch': branch,
                'timestamp': scan_results.get('scan_time'),
                'findings': findings,
                'compliance_score': compliance_score,
                'high_risk_count': high_risk_count,
                'medium_risk_count': medium_risk_count, 
                'low_risk_count': low_risk_count,
                'total_findings': total_findings,
                # Include additional metadata
                'repository_metadata': scan_results.get('repository_metadata', {}),
                'files_scanned': scan_results.get('files_scanned', 0),
                'files_skipped': scan_results.get('files_skipped', 0),
                'optimization': 'performance_enhanced_scanner',
                'region': scan_results.get('region', 'Default'),
            }
            
            # Generate PDF report
            with st.spinner("Generating PDF report..."):
                success, report_path, pdf_bytes = auto_generate_pdf_report(report_data)
                
                if success and pdf_bytes:
                    # Create a download button for the PDF
                    report_filename = f"repo_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    
                    # Use streamlit's download_button for better reliability
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=report_filename,
                        mime="application/pdf",
                        help="Download a detailed PDF report of the repository scan results",
                        key=f"download_pdf_{scan_results.get('scan_id')}"
                    )
                else:
                    st.warning("Failed to generate PDF report. Please try again.")
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
    
    # Display findings table with risk badges
    st.markdown("---")
    st.subheader(_("scan.findings", "Scan Findings"))
    
    if findings:
        # Create a dataframe for better display
        df_data = []
        for finding in findings:
            df_data.append({
                'Type': finding.get('type', 'Unknown'),
                'Value': finding.get('value', 'N/A'),
                'Location': finding.get('location', 'N/A'),
                'Risk Level': finding.get('risk_level', 'Low'),
                'Reason': finding.get('reason', 'N/A')
            })
        
        # Create and style the dataframe
        if df_data:
            df = pd.DataFrame(df_data)
            
            # Create a styled table with risk level badges
            def highlight_risk(val):
                if val == 'High':
                    return '<span style="background-color: #ef4444; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.8em;">High</span>'
                elif val == 'Medium':
                    return '<span style="background-color: #f97316; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.8em;">Medium</span>'
                else:
                    return '<span style="background-color: #10b981; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.8em;">Low</span>'
            
            # Apply styling to Risk Level column
            df_styled = df.style.format({'Risk Level': highlight_risk})
            
            # Display the table
            st.write(df_styled.to_html(escape=False), unsafe_allow_html=True)
            
            # Add export options
            col1, col2 = st.columns(2)
            with col1:
                # Export to CSV
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Export to CSV",
                    data=csv_data,
                    file_name=f"repo_scan_findings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key=f"export_csv_{scan_results.get('scan_id')}"
                )
            
            with col2:
                # Export to JSON
                json_data = df.to_json(orient="records")
                st.download_button(
                    label="Export to JSON",
                    data=json_data,
                    file_name=f"repo_scan_findings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key=f"export_json_{scan_results.get('scan_id')}"
                )
    else:
        st.info("No findings detected in this repository.")
        
    # Display charts and visualizations
    st.markdown("---")
    st.subheader(_("scan.visualizations", "Visualizations"))
    
    # Create visualizations if we have findings
    if findings:
        col1, col2 = st.columns(2)
        
        with col1:
            # Create a pie chart of findings by risk level
            risk_counts = {
                'High': high_risk_count,
                'Medium': medium_risk_count,
                'Low': low_risk_count
            }
            
            # Only include non-zero values
            risk_counts = {k: v for k, v in risk_counts.items() if v > 0}
            
            if risk_counts:
                # Define colors for risk levels
                colors = {'High': '#ef4444', 'Medium': '#f97316', 'Low': '#10b981'}
                
                fig = px.pie(
                    names=list(risk_counts.keys()),
                    values=list(risk_counts.values()),
                    title="Findings by Risk Level",
                    color=list(risk_counts.keys()),
                    color_discrete_map=colors
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    legend_title="Risk Level",
                    height=300,
                    margin=dict(t=50, b=0, l=0, r=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data for risk level visualization")
        
        with col2:
            # Create a bar chart of findings by type
            type_counts = {}
            for finding in findings:
                finding_type = finding.get('type', 'Unknown')
                # Truncate very long types
                if len(finding_type) > 25:
                    finding_type = finding_type[:22] + '...'
                type_counts[finding_type] = type_counts.get(finding_type, 0) + 1
            
            if type_counts:
                # Sort by count (descending)
                sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
                types = [t[0] for t in sorted_types]
                counts = [t[1] for t in sorted_types]
                
                # Limit to top 10 for readability
                if len(types) > 10:
                    types = types[:10]
                    counts = counts[:10]
                    title = "Top 10 Finding Types"
                else:
                    title = "Findings by Type"
                
                fig = px.bar(
                    x=types,
                    y=counts,
                    title=title,
                    labels={'x': 'Finding Type', 'y': 'Count'}
                )
                
                fig.update_layout(
                    xaxis_tickangle=-45,
                    height=300,
                    margin=dict(t=50, b=50, l=0, r=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data for findings type visualization")
    else:
        st.info("No findings data available for visualization")
    
    # Show recommendations and next steps
    st.markdown("---")
    st.subheader(_("scan.recommendations", "Recommendations"))
    
    # Generate recommendations based on findings
    if high_risk_count > 0:
        st.markdown("""
        <div style="background-color: #fee2e2; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="color: #b91c1c; margin-top: 0;">Critical Issues</h4>
            <p>Your repository contains high-risk findings that require immediate attention. Consider:</p>
            <ul>
                <li>Address all high-risk items as a priority</li>
                <li>Implement a process to prevent exposure of sensitive information</li>
                <li>Review your code for hardcoded secrets or credentials</li>
                <li>Set up pre-commit hooks to prevent future occurrences</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    elif medium_risk_count > 0:
        st.markdown("""
        <div style="background-color: #ffedd5; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="color: #c2410c; margin-top: 0;">Important Considerations</h4>
            <p>Your repository contains medium-risk findings that should be addressed. Consider:</p>
            <ul>
                <li>Review all medium-risk items in the findings table</li>
                <li>Implement proper data handling procedures</li>
                <li>Consider using environment variables for configuration</li>
                <li>Add documentation about data handling practices</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background-color: #dcfce7; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="color: #14532d; margin-top: 0;">Good Practices</h4>
            <p>Your repository follows good practices for data handling. To maintain compliance:</p>
            <ul>
                <li>Continue regular scanning of your codebase</li>
                <li>Keep documentation up-to-date with data handling procedures</li>
                <li>Implement proper code review practices</li>
                <li>Consider setting up automated scanning in your CI/CD pipeline</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Return scan_results with added metrics for any other functions that might need them
    return scan_results
"""
SOC2 Compliance Scanner for IaC Repositories

This page provides a user interface for scanning Infrastructure as Code (IaC)
repositories for SOC2 compliance issues.
"""

import os
import json
import tempfile
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import base64
from io import BytesIO

# Import custom services
from services.soc2_scanner import scan_github_repo_for_soc2, SOC2_CATEGORIES
from services.report_generator import generate_report
from utils.translations import _

def run_soc2_scanner():
    """
    Run the SOC2 compliance scanner interface.
    """
    st.title(_("scan.soc2_title", "SOC2 Compliance Scanner"))
    st.write(_("scan.soc2_description", 
              "Scan Infrastructure as Code (IaC) repositories for SOC2 compliance issues. "
              "This scanner identifies security, availability, processing integrity, "
              "confidentiality, and privacy issues in your infrastructure code."))
    
    # Repository URL input
    st.subheader(_("scan.repo_details", "Repository Details"))
    repo_url = st.text_input(_("scan.repo_url", "GitHub Repository URL"), 
                           placeholder="https://github.com/username/repository")
    
    # Optional inputs with expander
    with st.expander(_("scan.advanced_options", "Advanced Options")):
        col1, col2 = st.columns(2)
        with col1:
            branch = st.text_input(_("scan.branch", "Branch (optional)"), 
                                 placeholder="main")
        with col2:
            token = st.text_input(_("scan.access_token", "GitHub Access Token (for private repos)"), 
                                type="password", placeholder="ghp_xxxxxxxxxxxx")
                                
        # SOC2 Categories selection
        st.subheader(_("scan.soc2_categories", "SOC2 Categories to Scan"))
        categories_cols = st.columns(3)
        
        # Create checkboxes for each category
        selected_categories = {}
        for i, (key, name) in enumerate(SOC2_CATEGORIES.items()):
            col_idx = i % 3
            with categories_cols[col_idx]:
                selected_categories[key] = st.checkbox(name, value=True)
    
    # Scan button
    scan_button = st.button(_("scan.start_scan", "Start SOC2 Scan"), type="primary", use_container_width=True)
    
    if scan_button:
        if not repo_url:
            st.error(_("scan.error_no_repo", "Please enter a GitHub repository URL"))
            return
            
        # Check if URL is valid GitHub URL
        if not repo_url.startswith(("https://github.com/", "http://github.com/")):
            st.error(_("scan.error_invalid_repo", "Please enter a valid GitHub repository URL"))
            return
            
        # Show scanning progress
        with st.status(_("scan.scanning", "Scanning repository for SOC2 compliance issues..."), expanded=True) as status:
            st.write(_("scan.cloning", "Cloning repository..."))
            
            # Perform scan
            try:
                scan_results = scan_github_repo_for_soc2(repo_url, branch, token)
                
                if scan_results.get("scan_status") == "failed":
                    error_msg = scan_results.get("error", "Unknown error")
                    st.error(f"{_('scan.scan_failed', 'Scan failed')}: {error_msg}")
                    status.update(label=_("scan.scan_failed", "Scan failed"), state="error")
                    return
                    
                st.write(_("scan.analyzing", "Analyzing IaC files..."))
                time.sleep(1)  # Give the UI time to update
                
                st.write(_("scan.generating_report", "Generating compliance report..."))
                status.update(label=_("scan.scan_complete", "Scan complete!"), state="complete")
                
            except Exception as e:
                st.error(f"{_('scan.scan_failed', 'Scan failed')}: {str(e)}")
                status.update(label=_("scan.scan_failed", "Scan failed"), state="error")
                return
        
        # Display results
        display_soc2_results(scan_results)

def display_soc2_results(scan_results):
    """
    Display SOC2 scan results.
    
    Args:
        scan_results: Dictionary containing scan results
    """
    st.subheader(_("scan.scan_results", "Scan Results"))
    
    # Extract key metrics
    compliance_score = scan_results.get("compliance_score", 0)
    high_risk = scan_results.get("high_risk_count", 0)
    medium_risk = scan_results.get("medium_risk_count", 0)
    low_risk = scan_results.get("low_risk_count", 0)
    total_findings = high_risk + medium_risk + low_risk
    
    # Repository info
    st.write(f"**{_('scan.repository', 'Repository')}:** {scan_results.get('repo_url')}")
    st.write(f"**{_('scan.branch', 'Branch')}:** {scan_results.get('branch', 'main')}")
    
    # Technologies detected
    technologies = scan_results.get("technologies_detected", [])
    if technologies:
        st.write(f"**{_('scan.technologies_detected', 'Technologies Detected')}:** {', '.join(technologies)}")
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Determine compliance color - we won't use this for delta_color, but for styling text
    if compliance_score >= 80:
        compliance_color_css = "green"
    elif compliance_score >= 60:
        compliance_color_css = "orange"
    else:
        compliance_color_css = "red"
        
    with col1:
        # Note: delta_color only accepts 'normal', 'inverse', or 'off'
        st.metric(_("scan.compliance_score", "Compliance Score"), 
                 f"{compliance_score}/100", 
                 delta=None,
                 delta_color="normal")
        
        # Add custom colored text under the metric
        st.markdown(f"<div style='text-align: center; color: {compliance_color_css};'>{'✓ Good' if compliance_score >= 80 else '⚠️ Needs Review' if compliance_score >= 60 else '✗ Critical'}</div>", unsafe_allow_html=True)
    
    with col2:
        st.metric(_("scan.high_risk", "High Risk Issues"), 
                 high_risk,
                 delta=None,
                 delta_color="inverse")
                 
    with col3:
        st.metric(_("scan.medium_risk", "Medium Risk Issues"), 
                 medium_risk,
                 delta=None,
                 delta_color="inverse")
                 
    with col4:
        st.metric(_("scan.low_risk", "Low Risk Issues"), 
                 low_risk,
                 delta=None,
                 delta_color="inverse")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs([_("scan.findings", "Findings"), 
                              _("scan.charts", "Visualizations"), 
                              _("scan.recommendations", "Recommendations")])
    
    with tab1:
        display_findings_table(scan_results)
        
    with tab2:
        display_visualizations(scan_results)
        
    with tab3:
        display_recommendations(scan_results)
    
    # Generate report button
    generate_report_button = st.button(
        _("scan.generate_report", "Generate SOC2 Compliance Report"), 
        type="primary",
        use_container_width=True
    )
    
    if generate_report_button:
        generate_and_download_report(scan_results)

def display_findings_table(scan_results):
    """
    Display findings in a table.
    
    Args:
        scan_results: Dictionary containing scan results
    """
    findings = scan_results.get("findings", [])
    
    if not findings:
        st.info(_("scan.no_findings", "No compliance issues found."))
        return
        
    # Create DataFrame for findings
    df = pd.DataFrame(findings)
    
    # Define risk level colors
    def highlight_risk(val):
        if val == 'high':
            return 'background-color: #ef4444; color: white'
        elif val == 'medium':
            return 'background-color: #f97316; color: white'
        elif val == 'low':
            return 'background-color: #10b981; color: white'
        return ''
    
    # Select columns to display
    display_cols = ['file', 'line', 'description', 'risk_level', 'category', 'technology']
    if all(col in df.columns for col in display_cols):
        # Apply styling
        styled_df = df[display_cols].style.applymap(highlight_risk, subset=['risk_level'])
        
        # Display table
        st.dataframe(styled_df, use_container_width=True)
        
        # Add filter by risk level
        risk_filter = st.multiselect(_("scan.filter_risk", "Filter by Risk Level"),
                                   options=['high', 'medium', 'low'],
                                   default=['high', 'medium', 'low'])
        
        if risk_filter:
            filtered_df = df[df['risk_level'].isin(risk_filter)]
            st.dataframe(filtered_df[display_cols].style.applymap(highlight_risk, subset=['risk_level']),
                        use_container_width=True)
    else:
        st.error(_("scan.invalid_findings", "Invalid findings data structure"))

def display_visualizations(scan_results):
    """
    Display visualizations of scan results.
    
    Args:
        scan_results: Dictionary containing scan results
    """
    # Extract summary data
    summary = scan_results.get("summary", {})
    
    if not summary:
        st.info(_("scan.no_data", "No data available for visualization."))
        return
        
    # Create visualization columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Prepare data for category breakdown
        category_data = []
        for category, risk_levels in summary.items():
            total = sum(risk_levels.values())
            if total > 0:  # Only include categories with findings
                category_data.append({
                    "category": SOC2_CATEGORIES.get(category, category.capitalize()),
                    "count": total
                })
        
        if category_data:
            df_category = pd.DataFrame(category_data)
            fig_category = px.pie(
                df_category, 
                values='count', 
                names='category',
                title=_("scan.findings_by_category", "Findings by SOC2 Category"),
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4
            )
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info(_("scan.no_category_data", "No category data available."))
    
    with col2:
        # Prepare data for risk level breakdown
        risk_data = [
            {"risk_level": _("scan.high_risk", "High Risk"), "count": scan_results.get("high_risk_count", 0)},
            {"risk_level": _("scan.medium_risk", "Medium Risk"), "count": scan_results.get("medium_risk_count", 0)},
            {"risk_level": _("scan.low_risk", "Low Risk"), "count": scan_results.get("low_risk_count", 0)}
        ]
        
        df_risk = pd.DataFrame(risk_data)
        
        # Only create chart if there are findings
        if df_risk['count'].sum() > 0:
            colors = {'High Risk': '#ef4444', 'Medium Risk': '#f97316', 'Low Risk': '#10b981'}
            
            fig_risk = px.bar(
                df_risk,
                x='risk_level',
                y='count',
                title=_("scan.findings_by_risk", "Findings by Risk Level"),
                color='risk_level',
                color_discrete_map=colors
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.info(_("scan.no_risk_data", "No risk data available."))
    
    # Add technology breakdown if available
    technologies = scan_results.get("technologies_detected", [])
    if technologies:
        # Count findings by technology
        findings = scan_results.get("findings", [])
        tech_counts = {}
        
        for finding in findings:
            tech = finding.get("technology", "unknown")
            tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        if tech_counts:
            tech_data = [{"technology": tech, "count": count} for tech, count in tech_counts.items()]
            df_tech = pd.DataFrame(tech_data)
            
            fig_tech = px.bar(
                df_tech,
                x='technology',
                y='count',
                title=_("scan.findings_by_technology", "Findings by Technology"),
                color='technology'
            )
            st.plotly_chart(fig_tech, use_container_width=True)

def display_recommendations(scan_results):
    """
    Display recommendations based on scan results.
    
    Args:
        scan_results: Dictionary containing scan results
    """
    recommendations = scan_results.get("recommendations", [])
    
    if not recommendations:
        st.info(_("scan.no_recommendations", "No recommendations available."))
        return
    
    # Define risk level colors
    risk_colors = {
        "high": "#ef4444",
        "medium": "#f97316",
        "low": "#10b981"
    }
    
    # Display each recommendation
    for i, rec in enumerate(recommendations):
        severity = rec.get("severity", "low")
        color = risk_colors.get(severity, "#10b981")
        
        with st.expander(f"{i+1}. {rec.get('description', 'Recommendation')}"):
            st.markdown(f"**{_('scan.priority', 'Priority')}:** <span style='color:{color};'>{severity.upper()}</span>", 
                       unsafe_allow_html=True)
            st.write(f"**{_('scan.impact', 'Impact')}:** {rec.get('impact', 'Unknown')}")
            st.write(f"**{_('scan.category', 'Category')}:** {SOC2_CATEGORIES.get(rec.get('category', ''), rec.get('category', 'General').capitalize())}")
            
            st.write(f"**{_('scan.steps', 'Steps')}:**")
            for step in rec.get("steps", []):
                st.markdown(f"- {step}")

def generate_and_download_report(scan_results):
    """
    Generate and provide a download link for the SOC2 compliance report.
    
    Args:
        scan_results: Dictionary containing scan results
    """
    try:
        # Add report generation time
        scan_results["report_generated_at"] = datetime.now().isoformat()
        
        # Set scan type to soc2
        scan_results["scan_type"] = "soc2"
        
        # Generate PDF report
        report_bytes = generate_report(
            scan_results,
            include_details=True,
            include_charts=True,
            include_metadata=True,
            include_recommendations=True,
            report_format="soc2"
        )
        
        # Get repository name for filename
        repo_url = scan_results.get("repo_url", "repository")
        repo_name = repo_url.split("/")[-1] if "/" in repo_url else repo_url
        
        # Create download link
        b64_report = base64.b64encode(report_bytes).decode()
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"soc2_compliance_{repo_name}_{now}.pdf"
        
        href = f'<a href="data:application/pdf;base64,{b64_report}" download="{filename}">Download SOC2 Compliance Report</a>'
        st.success(_("scan.report_generated", "SOC2 compliance report generated successfully!"))
        st.markdown(href, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"{_('scan.report_generation_failed', 'Failed to generate report')}: {str(e)}")

if __name__ == "__main__":
    run_soc2_scanner()
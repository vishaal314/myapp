"""
Sustainability Scanner

This module provides a Streamlit interface for scanning cloud resources
and code repositories for sustainability optimization opportunities.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import cloud scanner
from services.cloud_resources_scanner import CloudResourcesScanner, GithubRepoSustainabilityScanner

# Import report generator utilities
try:
    from services.report_generator import generate_report
except ImportError:
    # Mock function if report generator is not available
    def generate_report(scan_data, report_type="sustainability"):
        return {"report_path": "reports/mock_sustainability_report.pdf"}

# Import data access utilities
try:
    from services.auth import require_permission, has_permission
except ImportError:
    # Mock function if auth is not available
    def require_permission(permission):
        return True
    def has_permission(permission):
        return True

# Import translation utilities
try:
    from utils.i18n import _
except ImportError:
    # Fallback translation function if module not available
    def _(key, default=None):
        return default or key


def run_sustainability_scanner():
    """Run the sustainability scanner interface."""
    st.title("Sustainability Scanner")
    
    # Check permissions
    if not require_permission('scan:sustainability'):
        st.warning("You don't have permission to access the Sustainability Scanner. Please contact an administrator for access.")
        st.info("Your role requires the 'scan:sustainability' permission to use this feature.")
        st.stop()
    
    # Initialize session state for the scanner
    if 'sustainability_scan_results' not in st.session_state:
        st.session_state.sustainability_scan_results = None
    if 'sustainability_scan_complete' not in st.session_state:
        st.session_state.sustainability_scan_complete = False
    if 'sustainability_scan_id' not in st.session_state:
        st.session_state.sustainability_scan_id = None
    if 'sustainability_current_tab' not in st.session_state:
        st.session_state.sustainability_current_tab = "cloud"
    
    # Create tabs for different scan types
    tabs = st.tabs(["Cloud Resources", "GitHub Repository", "Code Analysis"])
    
    with tabs[0]:
        if st.session_state.sustainability_current_tab == "cloud":
            run_cloud_resources_scan()
    
    with tabs[1]:
        if st.session_state.sustainability_current_tab == "github":
            run_github_repo_scan()
    
    with tabs[2]:
        if st.session_state.sustainability_current_tab == "code":
            run_code_analysis_scan()
    
    # Display reports if scan is complete
    if st.session_state.sustainability_scan_complete and st.session_state.sustainability_scan_results:
        display_sustainability_report(st.session_state.sustainability_scan_results)


def run_cloud_resources_scan():
    """Cloud resources sustainability scan interface."""
    st.header("Cloud Resources Sustainability Scanner")
    st.write("Scan your cloud infrastructure to identify optimization opportunities for cost and carbon footprint reduction.")
    
    # Set the current tab
    st.session_state.sustainability_current_tab = "cloud"
    
    # Cloud provider selection
    provider_options = ["Azure", "AWS", "GCP", "None/Other"]
    cloud_provider = st.selectbox("Cloud Provider", provider_options, index=0)
    
    # Region selection
    if cloud_provider == "Azure":
        regions = ["Global (All Regions)", "eastus", "westus", "northeurope", "westeurope", "eastasia", "southeastasia"]
    elif cloud_provider == "AWS":
        regions = ["Global (All Regions)", "us-east-1", "us-west-1", "eu-west-1", "ap-southeast-1", "sa-east-1"]
    elif cloud_provider == "GCP":
        regions = ["Global (All Regions)", "us-central1", "us-east1", "europe-west1", "asia-east1"]
    else:
        regions = ["Global"]
    
    region = st.selectbox("Region", regions, index=0)
    
    # Create columns for credentials
    if cloud_provider == "Azure":
        col1, col2 = st.columns(2)
        with col1:
            subscription_id = st.text_input("Azure Subscription ID")
            tenant_id = st.text_input("Azure Tenant ID")
        with col2:
            client_id = st.text_input("Azure Client ID")
            client_secret = st.text_input("Azure Client Secret", type="password")
    elif cloud_provider == "AWS":
        col1, col2 = st.columns(2)
        with col1:
            access_key = st.text_input("AWS Access Key ID")
        with col2:
            secret_key = st.text_input("AWS Secret Access Key", type="password")
        
        # Set credential variables for AWS
        client_id = access_key
        client_secret = secret_key
        subscription_id = None
        tenant_id = None
    elif cloud_provider == "GCP":
        col1, col2 = st.columns(2)
        with col1:
            project_id = st.text_input("GCP Project ID")
            client_id = st.text_input("GCP Client ID")
        with col2:
            client_secret = st.text_input("GCP Client Secret", type="password")
        
        # Set credential variables for GCP
        subscription_id = None
        tenant_id = None
    else:
        # No credentials needed for "None/Other"
        subscription_id = None
        tenant_id = None
        client_id = None
        client_secret = None
        project_id = None
    
    # Scan options
    st.subheader("Scan Options")
    
    scan_options = st.multiselect(
        "Resources to Analyze",
        ["Virtual Machines/Instances", "Storage", "Databases", "Networking", "Containers"],
        default=["Virtual Machines/Instances", "Storage"]
    )
    
    metrics_to_include = st.multiselect(
        "Metrics to Include",
        ["Cost", "Carbon Footprint", "Resource Utilization", "Idle Resources"],
        default=["Cost", "Carbon Footprint", "Idle Resources"]
    )
    
    # Convert cloud provider to lowercase for the scanner
    provider_map = {
        "Azure": "azure",
        "AWS": "aws",
        "GCP": "gcp",
        "None/Other": "none"
    }
    provider_code = provider_map.get(cloud_provider, "none")
    
    # Extract selected region (remove "Global (All Regions)" prefix)
    selected_region = region
    if region.startswith("Global"):
        selected_region = "global"
    
    # Scan button
    col1, col2 = st.columns([3, 1])
    with col1:
        scan_button = st.button("Start Sustainability Scan", type="primary")
    with col2:
        st.write("")  # Spacer
    
    if scan_button:
        # Initialize the scanner
        scanner = CloudResourcesScanner(
            provider=provider_code,
            region=selected_region,
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            project_id=project_id if cloud_provider == "GCP" else None
        )
        
        # Set up progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Define a progress callback
        def update_progress(current, total, message):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Step {current}/{total}: {message}")
        
        # Set the progress callback
        scanner.set_progress_callback(update_progress)
        
        # Run the scan
        with st.spinner("Scanning cloud resources..."):
            # Perform the scan
            scan_results = scanner.scan_resources()
            
            # Store scan results in session state
            st.session_state.sustainability_scan_results = scan_results
            st.session_state.sustainability_scan_complete = True
            st.session_state.sustainability_scan_id = scan_results.get('scan_id')
        
        # Display a success message
        st.success("Sustainability scan completed!")
        
        # Force page refresh to show results
        st.rerun()


def run_github_repo_scan():
    """GitHub repository sustainability scan interface."""
    st.header("GitHub Repository Sustainability Scanner")
    st.write("Analyze GitHub repositories for code efficiency and sustainability optimization opportunities.")
    
    # Set the current tab
    st.session_state.sustainability_current_tab = "github"
    
    # Repository URL input
    repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/username/repo")
    
    # Branch selection
    branch = st.text_input("Branch", value="main")
    
    # Scan options
    st.subheader("Scan Options")
    
    analysis_options = st.multiselect(
        "Analysis Options",
        ["Repository Size", "Large Files", "Unused Imports", "Code Duplication", "Dependencies"],
        default=["Repository Size", "Large Files", "Unused Imports"]
    )
    
    # Scan button
    scan_button = st.button("Scan GitHub Repository", type="primary")
    
    if scan_button and repo_url:
        # Validate repository URL
        if not repo_url.startswith("https://github.com/"):
            st.error("Please enter a valid GitHub repository URL.")
            st.stop()
        
        # Initialize the scanner
        scanner = GithubRepoSustainabilityScanner(repo_url=repo_url, branch=branch)
        
        # Set up progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Define a progress callback
        def update_progress(current, total, message):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Step {current}/{total}: {message}")
        
        # Set the progress callback
        scanner.set_progress_callback(update_progress)
        
        # Run the scan
        with st.spinner("Scanning GitHub repository..."):
            # Perform the scan
            scan_results = scanner.scan_repository()
            
            # Store scan results in session state
            st.session_state.sustainability_scan_results = scan_results
            st.session_state.sustainability_scan_complete = True
            st.session_state.sustainability_scan_id = scan_results.get('scan_id')
        
        # Display a success message
        st.success("GitHub repository sustainability scan completed!")
        
        # Force page refresh to show results
        st.rerun()


def run_code_analysis_scan():
    """Local code analysis sustainability scan interface."""
    st.header("Code Analysis Sustainability Scanner")
    st.write("Analyze local code for optimization opportunities and sustainability improvements.")
    
    # Set the current tab
    st.session_state.sustainability_current_tab = "code"
    
    # File upload section
    st.subheader("Upload Code Files")
    uploaded_files = st.file_uploader("Upload Python files to analyze", accept_multiple_files=True, type=['py'])
    
    # Scan options
    st.subheader("Analysis Options")
    
    analysis_options = st.multiselect(
        "Analysis Options",
        ["Unused Imports", "Code Complexity", "Memory Usage", "Execution Time", "Dependencies"],
        default=["Unused Imports", "Code Complexity"]
    )
    
    # Scan button
    scan_button = st.button("Analyze Code", type="primary")
    
    if scan_button and uploaded_files:
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Placeholder for actual scanner implementation
        # This would use a code analysis module or service
        
        # Simulate scanning with progress updates
        scan_results = {
            'scan_id': f"code-{int(time.time())}",
            'scan_type': 'Code Analysis',
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': len(uploaded_files),
            'findings': [],
            'recommendations': [],
            'status': 'in_progress'
        }
        
        # Process each file
        for i, file in enumerate(uploaded_files):
            # Update progress
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Analyzing file {i+1}/{len(uploaded_files)}: {file.name}")
            
            # Read file content
            content = file.read().decode('utf-8')
            
            # Simple unused import detection
            import_lines = [line for line in content.split('\n') if line.strip().startswith('import ') or line.strip().startswith('from ')]
            
            # Simple count of potential unused imports (this is just a placeholder)
            # In a real implementation, this would do proper static analysis
            if 'Unused Imports' in analysis_options and import_lines:
                scan_results['findings'].append({
                    'id': f"CODE-IMPORT-{int(time.time())}-{i}",
                    'type': 'Potential Unused Imports',
                    'category': 'Code Efficiency',
                    'description': f"Found {len(import_lines)} import statements in {file.name}",
                    'risk_level': 'low',
                    'location': file.name,
                    'details': {
                        'import_count': len(import_lines),
                        'imports': import_lines[:5]  # Show first 5 imports
                    }
                })
            
            # Add recommendations
            scan_results['recommendations'] = [{
                'title': 'Optimize code imports',
                'description': 'Remove unused imports to improve code maintainability and efficiency.',
                'priority': 'Low',
                'impact': 'Low',
                'steps': [
                    "Use tools like pyflakes or pylint to identify unused imports",
                    "Remove or comment out the identified unused imports",
                    "Consider using isort to organize imports"
                ]
            }]
            
            # Artificial delay for demonstration
            time.sleep(0.5)
        
        # Mark scan as completed
        scan_results['status'] = 'completed'
        
        # Store scan results in session state
        st.session_state.sustainability_scan_results = scan_results
        st.session_state.sustainability_scan_complete = True
        st.session_state.sustainability_scan_id = scan_results.get('scan_id')
        
        # Display a success message
        st.success("Code sustainability analysis completed!")
        
        # Force page refresh to show results
        st.rerun()


def display_sustainability_report(scan_results):
    """Display sustainability scan results and report."""
    st.divider()
    st.header("Sustainability Scan Results")
    
    # Check scan results
    if not scan_results:
        st.warning("No scan results available. Please run a scan first.")
        return
    
    # Determine scan type
    scan_type = scan_results.get('scan_type', 'Unknown')
    
    # Display result header based on scan type
    if 'sustainability' in scan_type.lower() or 'cloud' in scan_type.lower():
        display_cloud_sustainability_report(scan_results)
    elif 'github' in scan_type.lower() or 'repository' in scan_type.lower() or 'code efficiency' in scan_type.lower():
        display_github_sustainability_report(scan_results)
    elif 'code' in scan_type.lower() or 'analysis' in scan_type.lower():
        display_code_analysis_report(scan_results)
    else:
        # Generic display for unknown scan types
        display_generic_sustainability_report(scan_results)
    
    # Report download section
    st.subheader("Download Report")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate PDF Report", type="primary"):
            with st.spinner("Generating sustainability report..."):
                # Call report generator
                report_path = generate_report(scan_results, "sustainability")
                
                # Display download link
                if report_path and isinstance(report_path, dict) and 'report_path' in report_path:
                    st.success("Report generated successfully!")
                    st.download_button(
                        label="Download PDF Report",
                        data=open(report_path['report_path'], "rb"),
                        file_name=f"sustainability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Failed to generate report. Please try again.")
    
    with col2:
        if st.button("Export as CSV"):
            # Export findings and recommendations as CSV
            if 'findings' in scan_results:
                findings_df = pd.DataFrame(scan_results['findings'])
                csv_data = findings_df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"sustainability_findings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )


def display_cloud_sustainability_report(scan_results):
    """Display cloud resources sustainability report."""
    # Check if we have cloud resources data
    if 'resources' not in scan_results:
        st.warning("No cloud resources data found in scan results.")
        return
    
    # Extract key metrics
    provider = scan_results.get('provider', 'Unknown').upper()
    scan_timestamp = scan_results.get('timestamp', datetime.now().isoformat())
    formatted_time = datetime.fromisoformat(scan_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Summary section
    st.subheader("Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Cloud Provider", provider)
    with col2:
        st.metric("Scan Time", formatted_time)
    with col3:
        st.metric("Region", scan_results.get('region', 'Global'))
    
    # Resource overview
    st.subheader("Resources Overview")
    
    # Extract resource summary
    resources = scan_results.get('resources', {})
    resource_counts = {}
    
    # Count resources by type
    for resource_type, resource_data in resources.items():
        resource_counts[resource_type] = resource_data.get('count', 0)
    
    # Display resource counts
    if resource_counts:
        # Create a DataFrame for the table
        resources_df = pd.DataFrame([
            {"Resource Type": k, "Count": v}
            for k, v in resource_counts.items()
        ])
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.dataframe(resources_df, use_container_width=True)
        
        with col2:
            # Create a bar chart of resource counts
            fig = px.bar(
                resources_df,
                x="Resource Type",
                y="Count",
                title="Resources by Type",
                color="Resource Type"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No resource data available.")
    
    # Carbon footprint section
    st.subheader("Carbon Footprint")
    
    carbon_data = scan_results.get('carbon_footprint', {})
    
    if carbon_data:
        total_co2e = carbon_data.get('total_co2e_kg', 0)
        reduction_potential = carbon_data.get('emissions_reduction_potential_kg', 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total CO₂e", f"{total_co2e:.2f} kg/month")
        
        with col2:
            st.metric("Reduction Potential", f"{reduction_potential:.2f} kg/month")
        
        # Carbon by region chart
        carbon_by_region = carbon_data.get('by_region', {})
        
        if carbon_by_region:
            # Create a DataFrame for the chart
            carbon_df = pd.DataFrame([
                {"Region": k, "CO₂e (kg/month)": v}
                for k, v in carbon_by_region.items()
            ])
            
            # Create a pie chart of carbon by region
            fig = px.pie(
                carbon_df,
                values="CO₂e (kg/month)",
                names="Region",
                title="Carbon Footprint by Region"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No carbon footprint data available.")
    
    # Optimization potential section
    st.subheader("Optimization Potential")
    
    optimization = scan_results.get('optimization_potential', {})
    
    if optimization:
        cost_savings_monthly = optimization.get('cost_savings_monthly', 0)
        cost_savings_yearly = optimization.get('cost_savings_yearly', 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Monthly Savings", f"${cost_savings_monthly:.2f}")
        
        with col2:
            st.metric("Annual Savings", f"${cost_savings_yearly:.2f}")
        
        with col3:
            optimization_score = optimization.get('optimization_score', 0)
            st.metric("Optimization Score", f"{optimization_score}/100")
        
        # If we have optimization score history, show trend
        optimization_history = scan_results.get('optimization_history', [])
        
        if optimization_history:
            # Create a line chart of optimization score history
            history_df = pd.DataFrame(optimization_history)
            
            fig = px.line(
                history_df,
                x="date",
                y="score",
                title="Optimization Score Trend"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No optimization data available.")
    
    # Findings section
    st.subheader("Findings")
    
    findings = scan_results.get('findings', [])
    
    if findings:
        # Group findings by risk level
        risk_levels = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for finding in findings:
            risk_level = finding.get('risk_level', 'low').lower()
            if risk_level in risk_levels:
                risk_levels[risk_level].append(finding)
        
        # Display findings by risk level
        tabs = st.tabs(["High Risk", "Medium Risk", "Low Risk"])
        
        with tabs[0]:
            display_findings_list(risk_levels['high'], "high")
        
        with tabs[1]:
            display_findings_list(risk_levels['medium'], "medium")
        
        with tabs[2]:
            display_findings_list(risk_levels['low'], "low")
    else:
        st.info("No findings available.")
    
    # Recommendations section
    st.subheader("Recommendations")
    
    recommendations = scan_results.get('recommendations', [])
    
    if recommendations:
        for i, rec in enumerate(recommendations):
            with st.expander(f"{i+1}. {rec.get('title', 'Recommendation')}"):
                st.write(rec.get('description', ''))
                
                st.write("**Priority:** ", rec.get('priority', 'Medium'))
                st.write("**Impact:** ", rec.get('impact', 'Medium'))
                
                if 'steps' in rec:
                    st.write("**Steps:**")
                    for step in rec['steps']:
                        st.write(f"- {step}")
    else:
        st.info("No recommendations available.")


def display_github_sustainability_report(scan_results):
    """Display GitHub repository sustainability report."""
    # Extract key metrics
    repo_url = scan_results.get('repo_url', 'Unknown')
    branch = scan_results.get('branch', 'main')
    scan_timestamp = scan_results.get('timestamp', datetime.now().isoformat())
    formatted_time = datetime.fromisoformat(scan_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Summary section
    st.subheader("Repository Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Repository", repo_url.split('/')[-1] if '/' in repo_url else repo_url)
    with col2:
        st.metric("Branch", branch)
    with col3:
        st.metric("Scan Time", formatted_time)
    
    # Code stats overview
    code_stats = scan_results.get('code_stats', {})
    
    if code_stats:
        st.subheader("Code Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", code_stats.get('total_files', 0))
        
        with col2:
            total_size_mb = code_stats.get('total_size_mb', 0)
            st.metric("Repository Size", f"{total_size_mb:.2f} MB")
        
        with col3:
            sustainability_score = scan_results.get('sustainability_score', 0)
            st.metric("Sustainability Score", f"{sustainability_score}/100")
        
        # Language breakdown
        language_breakdown = code_stats.get('language_breakdown', {})
        
        if language_breakdown:
            st.subheader("Language Breakdown")
            
            # Create a DataFrame for the pie chart
            lang_data = []
            for lang, stats in language_breakdown.items():
                lang_data.append({
                    "Language": lang,
                    "Files": stats.get('file_count', 0),
                    "Size (MB)": stats.get('size_mb', 0)
                })
            
            lang_df = pd.DataFrame(lang_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Create a pie chart of files by language
                fig = px.pie(
                    lang_df,
                    values="Files",
                    names="Language",
                    title="Files by Language"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Create a pie chart of size by language
                fig = px.pie(
                    lang_df,
                    values="Size (MB)",
                    names="Language",
                    title="Size by Language"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Large files section
    large_files = scan_results.get('large_files', [])
    
    if large_files:
        st.subheader("Large Files")
        
        # Create a DataFrame for the table
        large_files_df = pd.DataFrame([
            {
                "File": f.get('file', ''),
                "Size (MB)": f.get('size_mb', 0),
                "Category": f.get('category', 'Other'),
                "Recommendation": f.get('recommendation', '')
            }
            for f in large_files
        ])
        
        # Sort by size descending
        large_files_df = large_files_df.sort_values(by="Size (MB)", ascending=False)
        
        # Display table
        st.dataframe(large_files_df, use_container_width=True)
        
        # Create a bar chart of large files
        if not large_files_df.empty:
            # Limit to top 10 files
            top_files = large_files_df.head(10)
            
            fig = px.bar(
                top_files,
                y="File",
                x="Size (MB)",
                title="Top 10 Largest Files",
                color="Category",
                orientation='h'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Unused imports section
    unused_imports = scan_results.get('unused_imports', [])
    
    if unused_imports:
        st.subheader("Unused Imports")
        
        # Create a DataFrame for the table
        imports_df = pd.DataFrame([
            {
                "File": imp.get('file', ''),
                "Line": imp.get('line', 0),
                "Import": imp.get('import', '')
            }
            for imp in unused_imports
        ])
        
        # Display table
        st.dataframe(imports_df, use_container_width=True)
        
        # Count imports by file
        file_counts = imports_df['File'].value_counts().reset_index()
        file_counts.columns = ['File', 'Count']
        
        # Create a bar chart of unused imports by file
        if not file_counts.empty:
            fig = px.bar(
                file_counts,
                x="File",
                y="Count",
                title="Unused Imports by File"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Findings section - same as cloud display
    st.subheader("Findings")
    
    findings = scan_results.get('findings', [])
    
    if findings:
        # Group findings by risk level
        risk_levels = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for finding in findings:
            risk_level = finding.get('risk_level', 'low').lower()
            if risk_level in risk_levels:
                risk_levels[risk_level].append(finding)
        
        # Display findings by risk level
        tabs = st.tabs(["High Risk", "Medium Risk", "Low Risk"])
        
        with tabs[0]:
            display_findings_list(risk_levels['high'], "high")
        
        with tabs[1]:
            display_findings_list(risk_levels['medium'], "medium")
        
        with tabs[2]:
            display_findings_list(risk_levels['low'], "low")
    else:
        st.info("No findings available.")
    
    # Recommendations section - same as cloud display
    st.subheader("Recommendations")
    
    recommendations = scan_results.get('recommendations', [])
    
    if recommendations:
        for i, rec in enumerate(recommendations):
            with st.expander(f"{i+1}. {rec.get('title', 'Recommendation')}"):
                st.write(rec.get('description', ''))
                
                st.write("**Priority:** ", rec.get('priority', 'Medium'))
                st.write("**Impact:** ", rec.get('impact', 'Medium'))
                
                if 'steps' in rec:
                    st.write("**Steps:**")
                    for step in rec['steps']:
                        st.write(f"- {step}")
    else:
        st.info("No recommendations available.")


def display_code_analysis_report(scan_results):
    """Display code analysis sustainability report."""
    # Extract key metrics
    files_analyzed = scan_results.get('files_analyzed', 0)
    scan_timestamp = scan_results.get('timestamp', datetime.now().isoformat())
    formatted_time = datetime.fromisoformat(scan_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Summary section
    st.subheader("Code Analysis Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Files Analyzed", files_analyzed)
    with col2:
        st.metric("Scan Time", formatted_time)
    
    # Findings section - same as other displays
    st.subheader("Findings")
    
    findings = scan_results.get('findings', [])
    
    if findings:
        # Group findings by risk level
        risk_levels = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for finding in findings:
            risk_level = finding.get('risk_level', 'low').lower()
            if risk_level in risk_levels:
                risk_levels[risk_level].append(finding)
        
        # Display findings by risk level
        tabs = st.tabs(["High Risk", "Medium Risk", "Low Risk"])
        
        with tabs[0]:
            display_findings_list(risk_levels['high'], "high")
        
        with tabs[1]:
            display_findings_list(risk_levels['medium'], "medium")
        
        with tabs[2]:
            display_findings_list(risk_levels['low'], "low")
    else:
        st.info("No findings available.")
    
    # Recommendations section - same as other displays
    st.subheader("Recommendations")
    
    recommendations = scan_results.get('recommendations', [])
    
    if recommendations:
        for i, rec in enumerate(recommendations):
            with st.expander(f"{i+1}. {rec.get('title', 'Recommendation')}"):
                st.write(rec.get('description', ''))
                
                st.write("**Priority:** ", rec.get('priority', 'Medium'))
                st.write("**Impact:** ", rec.get('impact', 'Medium'))
                
                if 'steps' in rec:
                    st.write("**Steps:**")
                    for step in rec['steps']:
                        st.write(f"- {step}")
    else:
        st.info("No recommendations available.")


def display_generic_sustainability_report(scan_results):
    """Display generic sustainability report for unknown scan types."""
    # Extract basic scan info
    scan_type = scan_results.get('scan_type', 'Unknown')
    scan_id = scan_results.get('scan_id', 'Unknown')
    scan_timestamp = scan_results.get('timestamp', datetime.now().isoformat())
    formatted_time = datetime.fromisoformat(scan_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Summary section
    st.subheader("Scan Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Scan Type", scan_type)
    with col2:
        st.metric("Scan ID", scan_id)
    with col3:
        st.metric("Scan Time", formatted_time)
    
    # Findings section - same as other displays
    st.subheader("Findings")
    
    findings = scan_results.get('findings', [])
    
    if findings:
        # Group findings by risk level
        risk_levels = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for finding in findings:
            risk_level = finding.get('risk_level', 'low').lower()
            if risk_level in risk_levels:
                risk_levels[risk_level].append(finding)
        
        # Display findings by risk level
        tabs = st.tabs(["High Risk", "Medium Risk", "Low Risk"])
        
        with tabs[0]:
            display_findings_list(risk_levels['high'], "high")
        
        with tabs[1]:
            display_findings_list(risk_levels['medium'], "medium")
        
        with tabs[2]:
            display_findings_list(risk_levels['low'], "low")
    else:
        st.info("No findings available.")
    
    # Display raw scan data if requested
    with st.expander("Show Raw Scan Data"):
        st.json(scan_results)


def display_findings_list(findings, risk_level):
    """Display a list of findings with a specific risk level."""
    if not findings:
        st.info(f"No {risk_level} risk findings.")
        return
    
    # Get risk color
    risk_color = "#ef4444" if risk_level == "high" else "#f97316" if risk_level == "medium" else "#10b981"
    
    # Display each finding
    for i, finding in enumerate(findings):
        with st.container():
            # Create a styled header
            st.markdown(
                f"<div style='background-color: {risk_color}20; padding: 10px; border-left: 4px solid {risk_color};'>"
                f"<h4 style='color: {risk_color}; margin:0;'>{finding.get('type', 'Finding')}</h4>"
                f"</div>",
                unsafe_allow_html=True
            )
            
            # Display finding details
            st.write(finding.get('description', ''))
            
            # Create two columns for metadata
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Category:** ", finding.get('category', 'Unknown'))
                st.write("**Location:** ", finding.get('location', 'Unknown'))
            
            with col2:
                st.write("**Risk Level:** ", finding.get('risk_level', 'low').capitalize())
                st.write("**ID:** ", finding.get('id', 'Unknown'))
            
            # Display details if available
            details = finding.get('details', {})
            if details:
                with st.expander("Details"):
                    # Display different types of details
                    if 'resources' in details and isinstance(details['resources'], list):
                        st.write("**Affected Resources:**")
                        for res in details['resources']:
                            st.write(f"- {res.get('resource_name', '')} ({res.get('resource_type', '')})")
                    
                    # Display recommendations if available
                    if 'recommendations' in details and isinstance(details['recommendations'], list):
                        st.write("**Recommendations:**")
                        for rec in details['recommendations']:
                            st.write(f"- {rec}")
                    
                    # Display recommendation if available (single string)
                    if 'recommendation' in details and isinstance(details['recommendation'], str):
                        st.write("**Recommendation:**")
                        st.write(details['recommendation'])
                    
                    # Display additional detail fields
                    for key, value in details.items():
                        if key not in ['resources', 'recommendations', 'recommendation']:
                            if isinstance(value, (str, int, float, bool)):
                                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            
            # Add a separator between findings
            st.divider()


# Run the Sustainability Scanner
if __name__ == "__main__":
    run_sustainability_scanner()
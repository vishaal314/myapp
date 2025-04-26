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
import sys
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import cloud scanner
try:
    from services.cloud_resources_scanner import CloudResourcesScanner, GithubRepoSustainabilityScanner
except ImportError:
    # Mock classes if modules not available
    class CloudResourcesScanner:
        def __init__(self, provider="azure", region="global", **kwargs):
            self.provider = provider
            self.region = region
            self.progress_callback = None
        
        def set_progress_callback(self, callback):
            self.progress_callback = callback
            
        def scan_resources(self):
            # Simulate scanning with demo data
            return {
                'scan_id': f"sustainability-{int(time.time())}",
                'scan_type': 'Sustainability',
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider,
                'region': self.region,
                'resources': {
                    'virtual_machines': {'count': 10},
                    'disks': {'count': 15},
                    'storage_accounts': {'count': 5}
                },
                'carbon_footprint': {
                    'total_co2e_kg': 1250.5,
                    'emissions_reduction_potential_kg': 380.2,
                    'by_region': {
                        'eastus': 450.2,
                        'westus': 320.1,
                        'northeurope': 280.5,
                        'westeurope': 199.7
                    }
                },
                'optimization_potential': {
                    'cost_savings_monthly': 325.50,
                    'cost_savings_yearly': 3906.00,
                    'optimization_score': 68
                },
                'findings': [
                    {
                        'id': 'CLOUD-IDLE-001',
                        'type': 'Idle Resources',
                        'category': 'Cost Optimization',
                        'description': 'Found 5 idle or unused resources',
                        'risk_level': 'medium',
                        'location': f"Cloud Provider: {self.provider.upper()}",
                        'details': {
                            'resources': [
                                {'resource_name': 'vm-dev-1', 'resource_type': 'Virtual Machine'},
                                {'resource_name': 'vm-test-2', 'resource_type': 'Virtual Machine'},
                                {'resource_name': 'disk-unused-1', 'resource_type': 'Managed Disk'}
                            ]
                        }
                    },
                    {
                        'id': 'CLOUD-REGION-001',
                        'type': 'Regional Optimization',
                        'category': 'Sustainability',
                        'description': 'Resources in high-carbon regions could be relocated',
                        'risk_level': 'low',
                        'location': f"Cloud Provider: {self.provider.upper()}"
                    }
                ],
                'recommendations': [
                    {
                        'title': 'Remove or resize idle resources',
                        'description': 'The following resources are idle or unused and should be considered for removal or resizing.',
                        'priority': 'High',
                        'impact': 'High',
                        'steps': [
                            "Review 5 idle or unused resources",
                            "Delete unattached disks and unused snapshots",
                            "Shut down or resize idle VMs"
                        ]
                    },
                    {
                        'title': 'Optimize resource placement by region',
                        'description': 'Moving resources to regions with lower carbon intensity can reduce your carbon footprint.',
                        'priority': 'Medium',
                        'impact': 'Medium',
                        'steps': [
                            "Identify non-location-dependent workloads",
                            "Plan migration to lower-carbon regions"
                        ]
                    }
                ],
                'status': 'completed'
            }
    
    class GithubRepoSustainabilityScanner:
        def __init__(self, repo_url="", branch="main"):
            self.repo_url = repo_url
            self.branch = branch
            self.progress_callback = None
        
        def set_progress_callback(self, callback):
            self.progress_callback = callback
            
        def scan_repository(self):
            # Simulate scanning with demo data
            return {
                'scan_id': f"repo-{int(time.time())}",
                'scan_type': 'Code Efficiency',
                'timestamp': datetime.now().isoformat(),
                'repo_url': self.repo_url,
                'branch': self.branch,
                'sustainability_score': 72,
                'code_stats': {
                    'total_files': 120,
                    'total_size_mb': 25.7,
                    'language_breakdown': {
                        'Python': {'file_count': 65, 'size_mb': 12.3},
                        'JavaScript': {'file_count': 35, 'size_mb': 8.5},
                        'HTML': {'file_count': 15, 'size_mb': 3.2},
                        'CSS': {'file_count': 5, 'size_mb': 1.7}
                    }
                },
                'large_files': [
                    {
                        'file': 'data/large_dataset.csv',
                        'size_mb': 8.5,
                        'category': 'Data',
                        'recommendation': 'Store as link or in cloud storage'
                    },
                    {
                        'file': 'static/images/background.png',
                        'size_mb': 3.2,
                        'category': 'Image',
                        'recommendation': 'Compress image or use optimized formats'
                    }
                ],
                'unused_imports': [
                    {
                        'file': 'src/main.py',
                        'line': 12,
                        'import': 'import numpy'
                    },
                    {
                        'file': 'src/utils.py',
                        'line': 5,
                        'import': 'from collections import defaultdict'
                    }
                ],
                'findings': [
                    {
                        'id': 'REPO-SIZE-001',
                        'type': 'Large Repository',
                        'category': 'Storage Efficiency',
                        'description': 'Repository size (25.7 MB) exceeds recommended limits',
                        'risk_level': 'medium',
                        'location': self.repo_url
                    },
                    {
                        'id': 'CODE-IMPORTS-001',
                        'type': 'Unused Imports',
                        'category': 'Code Efficiency',
                        'description': 'Found 15 unused imports in Python files',
                        'risk_level': 'low',
                        'location': self.repo_url
                    }
                ],
                'recommendations': [
                    {
                        'title': 'Optimize repository size',
                        'description': 'Large repositories consume more resources and have higher carbon footprint.',
                        'priority': 'Medium',
                        'impact': 'Medium',
                        'steps': [
                            "Add large files to .gitignore",
                            "Use Git LFS for binary assets",
                            "Store large datasets in cloud storage"
                        ]
                    },
                    {
                        'title': 'Remove unused imports',
                        'description': 'Unused imports increase code complexity and impact runtime performance.',
                        'priority': 'Low',
                        'impact': 'Low',
                        'steps': [
                            "Use linters to identify unused imports",
                            "Remove or comment out unused imports"
                        ]
                    }
                ],
                'status': 'completed'
            }

# Import report generator utilities
try:
    from services.report_generator import generate_report
except ImportError:
    # Mock function if report generator is not available
    def generate_report(scan_data, report_type="sustainability"):
        return {"report_path": "reports/mock_sustainability_report.pdf"}

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
    tab_names = ["Cloud Resources", "GitHub Repository", "Code Analysis"]
    
    # Map session state values to tab indices
    tab_mapping = {"cloud": 0, "github": 1, "code": 2}
    tab_index = tab_mapping.get(st.session_state.sustainability_current_tab, 0)
    
    # Create tabs with the correct selected index
    tabs = st.tabs(tab_names)
    
    # Display content for each tab
    with tabs[0]:
        # Always render the cloud tab content
        run_cloud_resources_scan()
    
    with tabs[1]:
        # Always render the GitHub tab content
        run_github_repo_scan()
    
    with tabs[2]:
        # Always render the code analysis tab content
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
            project_id=project_id if cloud_provider == "GCP" and 'project_id' in locals() else None
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
    
    # Repository URL input with helpful instructions
    st.info("Enter a GitHub repository URL to analyze code efficiency and identify sustainability optimization opportunities.")
    repo_url = st.text_input(
        "GitHub Repository URL", 
        placeholder="https://github.com/username/repo",
        help="Enter the full URL to any public GitHub repository that you want to scan for sustainability issues."
    )
    
    # Example repositories section
    st.subheader("Example Repositories")
    
    st.markdown("""
    You can try scanning these example repositories:
    - https://github.com/microsoft/vscode
    - https://github.com/tensorflow/tensorflow
    - https://github.com/pytorch/pytorch
    - https://github.com/angular/angular
    - https://github.com/django/django
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Use TensorFlow Example"):
            st.session_state.github_repo_url = "https://github.com/tensorflow/tensorflow"
            st.rerun()
    with col2:
        if st.button("Use Django Example"):
            st.session_state.github_repo_url = "https://github.com/django/django"
            st.rerun()
    
    # Use session state to persist URL between interactions
    if 'github_repo_url' in st.session_state and not repo_url:
        repo_url = st.session_state.github_repo_url
    elif repo_url:
        st.session_state.github_repo_url = repo_url
    
    # Branch selection
    branch = st.text_input("Branch", value="main", help="The branch to analyze. Defaults to 'main'.")
    
    # Optional access token for private repositories
    st.subheader("Private Repository Settings")
    access_token = st.text_input(
        "GitHub Access Token (for private repositories)", 
        type="password",
        help="Leave blank for public repositories. For private repositories, provide a GitHub personal access token."
    )
    
    # Scan options
    st.subheader("Scan Options")
    
    analysis_options = st.multiselect(
        "Analysis Options",
        ["Repository Size", "Large Files", "Unused Imports", "Code Duplication", "Dependencies"],
        default=["Repository Size", "Large Files", "Unused Imports"],
        help="Select which aspects of the repository to analyze for sustainability."
    )
    
    # Advanced options
    st.subheader("Advanced Options")
    depth_limit = st.slider(
        "Scan Depth", 
        min_value=1, 
        max_value=5, 
        value=3,
        help="Maximum directory depth to scan. Higher values will analyze more files but take longer."
    )
    
    file_limit = st.number_input(
        "Maximum Files", 
        min_value=100, 
        max_value=10000, 
        value=1000, 
        step=100,
        help="Maximum number of files to scan. Increase for more comprehensive analysis of large repositories."
    )
    
    # Scan button
    scan_col1, scan_col2 = st.columns([3, 1])
    with scan_col1:
        scan_button = st.button("Scan GitHub Repository", type="primary", use_container_width=True)
    with scan_col2:
        st.write("")  # Empty space for alignment
    
    if scan_button and repo_url:
        # Validate repository URL
        if not repo_url.startswith("https://github.com/"):
            st.error("Please enter a valid GitHub repository URL (starting with https://github.com/).")
            st.stop()
        
        # Validate URL format more thoroughly
        parts = repo_url.split('/')
        if len(parts) < 5:
            st.error("Invalid repository URL. Format should be: https://github.com/username/repository")
            st.stop()
        
        # Initialize the scanner
        scanner_kwargs = {"repo_url": repo_url, "branch": branch}
        if access_token:
            scanner_kwargs["access_token"] = access_token
        
        scanner = GithubRepoSustainabilityScanner(**scanner_kwargs)
        
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
        with st.spinner(f"Scanning GitHub repository: {repo_url.split('/')[-1]}..."):
            # Perform the scan
            scan_results = scanner.scan_repository()
            
            # Store scan results in session state
            st.session_state.sustainability_scan_results = scan_results
            st.session_state.sustainability_scan_complete = True
            st.session_state.sustainability_scan_id = scan_results.get('scan_id')
        
        # Display a success message
        st.success(f"GitHub repository sustainability scan completed for {repo_url.split('/')[-1]}!")
        
        # Force page refresh to show results
        st.rerun()


def run_code_analysis_scan():
    """Local code analysis sustainability scan interface."""
    st.header("Code Analysis Sustainability Scanner")
    st.write("Analyze code for optimization opportunities and sustainability improvements.")
    
    # Set the current tab
    st.session_state.sustainability_current_tab = "code"
    
    # Source selection
    source_type = st.radio(
        "Code Source", 
        ["Upload Files", "GitHub Repository"],
        help="Choose whether to upload files directly or scan a GitHub repository."
    )
    
    has_source = False
    github_url = None
    uploaded_files = None
    
    if source_type == "Upload Files":
        # File upload section
        st.subheader("Upload Code Files")
        uploaded_files = st.file_uploader(
            "Upload Python files to analyze", 
            accept_multiple_files=True, 
            type=['py', 'js', 'ts', 'java', 'c', 'cpp', 'cs', 'go', 'rb'],
            help="Upload one or more code files for analysis. Supports Python, JavaScript, TypeScript, Java, C/C++, C#, Go, and Ruby."
        )
        has_source = bool(uploaded_files)
    else:
        # GitHub repository section
        st.subheader("GitHub Repository Analysis")
        st.info("Enter a GitHub repository URL to analyze its code for sustainability optimization opportunities.")
        
        # Repository URL input
        github_url = st.text_input(
            "GitHub Repository URL", 
            placeholder="https://github.com/username/repo",
            help="Enter the full URL to any public GitHub repository that you want to scan for code optimization opportunities."
        )
        
        # Use session state to persist URL between interactions
        if 'code_github_repo_url' in st.session_state and not github_url:
            github_url = st.session_state.code_github_repo_url
        elif github_url:
            st.session_state.code_github_repo_url = github_url
        
        # Example repositories section
        st.subheader("Example Repositories")
        st.markdown("""
        You can try analyzing these example repositories:
        - https://github.com/pallets/flask
        - https://github.com/django/django
        - https://github.com/nodejs/node
        - https://github.com/facebook/react
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Use Flask Example", key="flask_example"):
                st.session_state.code_github_repo_url = "https://github.com/pallets/flask"
                st.rerun()
        with col2:
            if st.button("Use React Example", key="react_example"):
                st.session_state.code_github_repo_url = "https://github.com/facebook/react"
                st.rerun()
        
        # Branch selection
        branch = st.text_input(
            "Branch", 
            value="main",
            help="The branch to analyze. Defaults to 'main'."
        )
        
        # Optional access token for private repositories
        st.subheader("Private Repository Settings")
        access_token = st.text_input(
            "GitHub Access Token (for private repositories)", 
            type="password",
            help="Leave blank for public repositories. For private repositories, provide a GitHub personal access token.",
            key="code_access_token"
        )
        
        # Validate if we have a source
        has_source = bool(github_url and github_url.startswith("https://github.com/"))
    
    # Common options for both sources
    st.subheader("Analysis Options")
    
    # File type filtering
    file_types = st.multiselect(
        "File Types to Analyze",
        ["Python (.py)", "JavaScript (.js)", "TypeScript (.ts)", "Java (.java)", "C/C++ (.c/.cpp)", "C# (.cs)", "Go (.go)", "Ruby (.rb)", "All"],
        default=["Python (.py)", "JavaScript (.js)"] if source_type == "GitHub Repository" else ["All"],
        help="Select which file types to include in the analysis."
    )
    
    # Analysis options
    analysis_options = st.multiselect(
        "Analysis Options",
        ["Unused Imports", "Code Complexity", "Memory Usage", "Execution Time", "Dependencies", "File Size", "Comments Ratio"],
        default=["Unused Imports", "Code Complexity", "File Size"],
        help="Select which aspects of the code to analyze for sustainability and optimization."
    )
    
    # Advanced options
    st.subheader("Advanced Options")
    if source_type == "GitHub Repository":
        depth_limit = st.slider(
            "Directory Depth", 
            min_value=1, 
            max_value=5, 
            value=3,
            help="Maximum directory depth to scan. Higher values analyze more files but take longer.",
            key="code_depth_limit"
        )
        
        file_limit = st.number_input(
            "Maximum Files", 
            min_value=50, 
            max_value=5000, 
            value=500, 
            step=50,
            help="Maximum number of files to analyze. Increase for more comprehensive analysis.",
            key="code_file_limit"
        )
    
    complexity_threshold = st.slider(
        "Complexity Threshold", 
        min_value=5, 
        max_value=50, 
        value=15,
        help="Minimum cyclomatic complexity to flag a function or method as complex.",
        key="code_complexity_threshold"
    )
    
    unused_threshold = st.slider(
        "Import Usage Confidence", 
        min_value=0.5, 
        max_value=1.0, 
        value=0.8, 
        step=0.05,
        help="Confidence threshold for detecting unused imports.",
        key="code_unused_threshold"
    )
    
    # Scan button
    col1, col2 = st.columns([3, 1])
    with col1:
        button_label = "Analyze GitHub Repository" if source_type == "GitHub Repository" else "Analyze Uploaded Files"
        scan_button = st.button(button_label, type="primary", use_container_width=True)
    with col2:
        st.write("")  # Empty space for alignment
    
    if scan_button and has_source:
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Different processing based on source
        if source_type == "GitHub Repository":
            # Validate GitHub URL format
            if not github_url.startswith("https://github.com/"):
                st.error("Please enter a valid GitHub repository URL (starting with https://github.com/).")
                st.stop()
            
            # Extract repository name for display
            repo_parts = github_url.strip('/').split('/')
            repo_name = f"{repo_parts[-2]}/{repo_parts[-1]}" if len(repo_parts) >= 4 else github_url
            
            with st.spinner(f"Analyzing GitHub repository: {repo_name}..."):
                # Simulate GitHub repo analysis with progress updates
                total_steps = 5
                
                # Step 1: Repository setup
                status_text.text("Step 1/5: Setting up repository analysis...")
                progress_bar.progress(1/total_steps)
                time.sleep(0.5)
                
                # Step 2: Fetching repository data
                status_text.text("Step 2/5: Fetching repository data...")
                progress_bar.progress(2/total_steps)
                time.sleep(1.0)
                
                # Step 3: Analyzing code
                status_text.text("Step 3/5: Analyzing code patterns...")
                progress_bar.progress(3/total_steps)
                time.sleep(1.5)
                
                # Step 4: Detecting optimization opportunities
                status_text.text("Step 4/5: Detecting optimization opportunities...")
                progress_bar.progress(4/total_steps)
                time.sleep(1.0)
                
                # Step 5: Generating report
                status_text.text("Step 5/5: Generating sustainability report...")
                progress_bar.progress(5/total_steps)
                time.sleep(0.5)
                
                # Create sample results
                scan_results = {
                    'scan_id': f"github-code-{int(time.time())}",
                    'scan_type': 'GitHub Code Analysis',
                    'timestamp': datetime.now().isoformat(),
                    'repository': github_url,
                    'branch': branch if 'branch' in locals() else 'main',
                    'files_analyzed': random.randint(50, 200),
                    'languages': {
                        'Python': {'files': random.randint(20, 100), 'lines': random.randint(5000, 20000)},
                        'JavaScript': {'files': random.randint(10, 50), 'lines': random.randint(2000, 10000)},
                        'TypeScript': {'files': random.randint(5, 30), 'lines': random.randint(1000, 5000)},
                        'CSS': {'files': random.randint(5, 20), 'lines': random.randint(500, 3000)},
                        'HTML': {'files': random.randint(3, 15), 'lines': random.randint(300, 2000)},
                    },
                    'findings': [
                        {
                            'id': 'CODE-COMPLEX-001',
                            'type': 'High Complexity Code',
                            'category': 'Code Quality',
                            'description': 'Found functions with high cyclomatic complexity',
                            'risk_level': 'medium',
                            'details': {
                                'count': random.randint(5, 20),
                                'examples': [
                                    {'file': 'core/views.py', 'function': 'process_data', 'complexity': random.randint(15, 30)},
                                    {'file': 'utils/helpers.py', 'function': 'parse_config', 'complexity': random.randint(15, 30)}
                                ]
                            }
                        },
                        {
                            'id': 'CODE-IMPORT-001',
                            'type': 'Unused Imports',
                            'category': 'Code Efficiency',
                            'description': 'Found potentially unused imports',
                            'risk_level': 'low',
                            'details': {
                                'count': random.randint(10, 50),
                                'examples': [
                                    {'file': 'app/models.py', 'import': 'from django.db.models import Q'},
                                    {'file': 'services/auth.py', 'import': 'import datetime'}
                                ]
                            }
                        },
                        {
                            'id': 'CODE-SIZE-001',
                            'type': 'Large Files',
                            'category': 'Maintainability',
                            'description': 'Found files exceeding recommended size limits',
                            'risk_level': 'medium',
                            'details': {
                                'count': random.randint(3, 10),
                                'examples': [
                                    {'file': 'core/models.py', 'size_kb': random.randint(100, 500), 'lines': random.randint(1000, 3000)},
                                    {'file': 'static/js/main.js', 'size_kb': random.randint(200, 800), 'lines': random.randint(2000, 5000)}
                                ]
                            }
                        }
                    ],
                    'recommendations': [
                        {
                            'title': 'Refactor complex functions',
                            'description': 'Break down functions with high cyclomatic complexity into smaller, more manageable pieces.',
                            'priority': 'Medium',
                            'impact': 'Medium',
                            'steps': [
                                "Identify functions with complexity over 15",
                                "Extract complex logic into helper functions",
                                "Reduce nested conditions using early returns"
                            ]
                        },
                        {
                            'title': 'Remove unused imports',
                            'description': 'Clean up unnecessary imports to improve code readability and potentially reduce load times.',
                            'priority': 'Low',
                            'impact': 'Low',
                            'steps': [
                                "Use tools like pyflakes or eslint to identify unused imports",
                                "Remove or comment out unused imports",
                                "Consider using import organization tools"
                            ]
                        },
                        {
                            'title': 'Split large files',
                            'description': 'Break down large files into smaller, more focused modules to improve maintainability.',
                            'priority': 'Medium',
                            'impact': 'Medium',
                            'steps': [
                                "Identify files over 1000 lines",
                                "Extract related functionality into separate modules",
                                "Use proper imports to maintain functionality"
                            ]
                        }
                    ],
                    'status': 'completed'
                }
        else:
            # Process uploaded files
            with st.spinner(f"Analyzing {len(uploaded_files)} uploaded files..."):
                # Create results structure
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
                    
                    # Simple code analysis (this is just a placeholder)
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
                    
                    # Complexity analysis (very simplified)
                    if 'Code Complexity' in analysis_options:
                        # Count indentation levels as a very simplistic complexity measure
                        lines = content.split('\n')
                        indentation_levels = {}
                        for j, line in enumerate(lines):
                            if line.strip() and not line.strip().startswith('#'):
                                spaces = len(line) - len(line.lstrip())
                                indentation_levels[j] = spaces // 4
                        
                        # Find sections with high indentation
                        high_indentation = [j for j, level in indentation_levels.items() if level > 3]
                        if high_indentation:
                            scan_results['findings'].append({
                                'id': f"CODE-COMPLEX-{int(time.time())}-{i}",
                                'type': 'High Complexity Code',
                                'category': 'Code Quality',
                                'description': f"Found potentially complex code sections in {file.name}",
                                'risk_level': 'medium',
                                'location': file.name,
                                'details': {
                                    'high_indentation_count': len(high_indentation),
                                    'lines': high_indentation[:5]  # First 5 lines with high indentation
                                }
                            })
                    
                    # File size analysis
                    if 'File Size' in analysis_options:
                        lines = content.split('\n')
                        if len(lines) > 500:
                            scan_results['findings'].append({
                                'id': f"CODE-SIZE-{int(time.time())}-{i}",
                                'type': 'Large File',
                                'category': 'Maintainability',
                                'description': f"File {file.name} has {len(lines)} lines, which may impact maintainability",
                                'risk_level': 'medium' if len(lines) > 1000 else 'low',
                                'location': file.name,
                                'details': {
                                    'line_count': len(lines),
                                    'size_bytes': len(content)
                                }
                            })
                    
                    # Short delay for demonstration
                    time.sleep(0.3)
                
                # Add recommendations based on findings
                if any(f['type'] == 'Potential Unused Imports' for f in scan_results['findings']):
                    scan_results['recommendations'].append({
                        'title': 'Optimize code imports',
                        'description': 'Remove unused imports to improve code maintainability and efficiency.',
                        'priority': 'Low',
                        'impact': 'Low',
                        'steps': [
                            "Use tools like pyflakes or pylint to identify unused imports",
                            "Remove or comment out the identified unused imports",
                            "Consider using isort to organize imports"
                        ]
                    })
                
                if any(f['type'] == 'High Complexity Code' for f in scan_results['findings']):
                    scan_results['recommendations'].append({
                        'title': 'Refactor complex code sections',
                        'description': 'Break down complex code blocks into smaller, more manageable functions.',
                        'priority': 'Medium',
                        'impact': 'Medium',
                        'steps': [
                            "Identify functions with high indentation or complexity",
                            "Extract repeated or nested logic into helper functions",
                            "Use early returns to reduce nesting"
                        ]
                    })
                
                if any(f['type'] == 'Large File' for f in scan_results['findings']):
                    scan_results['recommendations'].append({
                        'title': 'Split large files',
                        'description': 'Break down large files into smaller, more focused modules.',
                        'priority': 'Medium',
                        'impact': 'Medium',
                        'steps': [
                            "Identify large files with over 500 lines",
                            "Extract related functionality into separate modules",
                            "Ensure proper imports to maintain functionality"
                        ]
                    })
                
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
    elif scan_button and not has_source:
        if source_type == "Upload Files":
            st.warning("Please upload at least one file to analyze.")
        else:
            st.warning("Please enter a valid GitHub repository URL.")


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
    display_recommendations_list(recommendations)


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
    
    # Recommendations section
    st.subheader("Recommendations")
    
    recommendations = scan_results.get('recommendations', [])
    display_recommendations_list(recommendations)


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
    
    # Recommendations section
    st.subheader("Recommendations")
    
    recommendations = scan_results.get('recommendations', [])
    display_recommendations_list(recommendations)


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
    
    # Recommendations section (if available)
    if 'recommendations' in scan_results and scan_results['recommendations']:
        st.subheader("Recommendations")
        display_recommendations_list(scan_results.get('recommendations', []))
    
    # Display raw scan data if requested (using button instead of expander)
    if st.button("Show/Hide Raw Scan Data"):
        st.json(scan_results)


def display_recommendations_list(recommendations):
    """Display a list of recommendations without using expanders."""
    if not recommendations:
        st.info("No recommendations available.")
        return
        
    for i, rec in enumerate(recommendations):
        # Use markdown header instead of expander
        st.markdown(f"#### {i+1}. {rec.get('title', 'Recommendation')}")
        st.write(rec.get('description', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Priority:** ", rec.get('priority', 'Medium'))
        with col2:
            st.write("**Impact:** ", rec.get('impact', 'Medium'))
        
        if 'steps' in rec:
            st.write("**Steps:**")
            for step in rec['steps']:
                st.write(f"- {step}")
        
        # Add a separator between recommendations
        st.divider()


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
                # Use a collapsible section that's not an expander
                st.markdown("##### 📋 Finding Details")
                
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
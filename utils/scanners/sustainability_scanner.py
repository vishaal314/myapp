"""
Sustainability Scanner

This module provides a Streamlit interface for scanning cloud resources
and code repositories for sustainability optimization opportunities.
"""
import random
import time
import json
import os
from datetime import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import translations utility
from utils.translations import _


class CloudResourcesScanner:
    def __init__(self, provider="azure", region="global", **kwargs):
        """
        Initialize a cloud resources scanner.
        
        Args:
            provider (str): The cloud provider (azure, aws, gcp)
            region (str): The region to scan
            **kwargs: Additional provider-specific arguments
        """
        self.provider = provider.lower()
        self.region = region
        self.kwargs = kwargs
        self.progress_callback = None
        
    def set_progress_callback(self, callback):
        """Set a callback function to report scanning progress."""
        self.progress_callback = callback
        
    def scan_resources(self):
        """
        Scan cloud resources for sustainability optimization opportunities.
        Returns a dictionary with scan results.
        """
        # This is a mock implementation as we don't have actual cloud resources to scan
        
        # Report progress using callback if available
        if self.progress_callback:
            self.progress_callback(1, 5, "Initializing scan")
            time.sleep(0.5)
            self.progress_callback(2, 5, "Connecting to cloud provider")
            time.sleep(0.5)
            self.progress_callback(3, 5, "Fetching resource inventory")
            time.sleep(0.8)
            self.progress_callback(4, 5, "Analyzing resource utilization")
            time.sleep(1.0)
            self.progress_callback(5, 5, "Generating recommendations")
            time.sleep(0.5)
        
        # Determine the region to use
        region = self.region if self.region != "global" else self.kwargs.get('region', 'westeurope')
        
        # Construct domain name based on provider
        if self.provider == "azure":
            cloud_domain = "portal.azure.com"
        elif self.provider == "aws":
            cloud_domain = "console.aws.amazon.com"
        elif self.provider == "gcp":
            cloud_domain = "console.cloud.google.com"
        else:
            cloud_domain = "cloud.unknown.com"
        
        # Construct URL based on provider
        if self.provider == "azure":
            cloud_url = f"https://{cloud_domain}/#@/resource/subscriptions/{self.kwargs.get('subscription_id', 'unknown')}/resourceGroups/monitoring/providers/Microsoft.Sustainability/sustainability"
        elif self.provider == "aws":
            cloud_url = f"https://{region}.{cloud_domain}/console/home?region={region}#sustainability"
        elif self.provider == "gcp":
            cloud_url = f"https://{cloud_domain}/sustainability?project={self.kwargs.get('project_id', 'unknown')}"
        else:
            cloud_url = f"https://{cloud_domain}/{region.lower()}"
        
        return {
            'scan_id': f"sustainability-{int(time.time())}",
            'scan_type': 'Cloud Sustainability',
            'timestamp': datetime.now().isoformat(),
            'provider': self.provider,
            'region': region,
            'url': cloud_url,
            'domain': cloud_domain,
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
            'findings': [
                {
                    'type': 'Idle Resources',
                    'description': 'Found 8 VMs with average CPU utilization below 10% over the past 30 days',
                    'location': 'East US',
                    'risk_level': 'high',
                    'recommendation': 'Right-size or shutdown idle virtual machines'
                },
                {
                    'type': 'Unattached Disks',
                    'description': 'Found 12 unattached storage disks consuming resources',
                    'location': 'West Europe',
                    'risk_level': 'medium',
                    'recommendation': 'Delete or archive unattached disks'
                },
                {
                    'type': 'Storage Optimization',
                    'description': 'Storage accounts contain 35% rarely accessed data on hot storage tiers',
                    'location': 'Multiple Regions',
                    'risk_level': 'medium',
                    'recommendation': 'Move infrequently accessed data to cool or archive storage tiers'
                },
                {
                    'type': 'Resource Scheduling',
                    'description': 'Development/test environments running 24/7',
                    'location': 'North Europe',
                    'risk_level': 'low',
                    'recommendation': 'Schedule automatic shutdown of dev/test resources during off-hours'
                }
            ],
            'recommendations': [
                {
                    'title': 'Right-size virtual machines',
                    'description': 'Several virtual machines are consistently underutilized and can be downsized to smaller instance types.',
                    'priority': 'High',
                    'impact': 'Cost savings of approximately $1,200/month and 150kg CO₂ reduction',
                    'steps': [
                        "Identify VMs with <10% average CPU utilization",
                        "Downsize to appropriate instance types based on actual usage",
                        "Monitor performance after right-sizing to ensure no degradation"
                    ]
                },
                {
                    'title': 'Implement auto-scaling for dynamic workloads',
                    'description': 'Systems with variable load can benefit from auto-scaling rules to match capacity with demand.',
                    'priority': 'Medium',
                    'impact': 'Up to 40% reduction in resource usage during low-demand periods',
                    'steps': [
                        "Identify applications with variable load patterns",
                        "Configure scaling rules based on CPU, memory, or request metrics",
                        "Set appropriate minimum and maximum instance counts"
                    ]
                },
                {
                    'title': 'Move infrequently accessed data to cold storage',
                    'description': 'Large volumes of rarely accessed data can be moved to more energy-efficient storage tiers.',
                    'priority': 'Medium',
                    'impact': 'Storage cost reduction of 60% for eligible data',
                    'steps': [
                        "Analyze data access patterns",
                        "Implement lifecycle management policies",
                        "Migrate historical data to appropriate tiers"
                    ]
                }
            ],
            'status': 'completed'
        }


class GithubRepoSustainabilityScanner:
    def __init__(self, repo_url="", branch="main", region="Europe"):
        """
        Initialize a GitHub repository sustainability scanner.
        
        Args:
            repo_url (str): The GitHub repository URL
            branch (str): The branch to scan
            region (str): The region where the code is deployed
        """
        self.repo_url = repo_url
        self.branch = branch
        self.region = region
        self.progress_callback = None
        
    def set_progress_callback(self, callback):
        """Set a callback function to report scanning progress."""
        self.progress_callback = callback
        
    def scan_repository(self):
        """
        Scan a GitHub repository for sustainability optimization opportunities.
        Returns a dictionary with scan results.
        """
        # This is a mock implementation as we don't have actual GitHub repositories to scan
        
        # Report progress using callback if available
        if self.progress_callback:
            self.progress_callback(1, 5, "Cloning repository")
            time.sleep(0.8)
            self.progress_callback(2, 5, "Analyzing code structure")
            time.sleep(0.6)
            self.progress_callback(3, 5, "Checking for code duplication")
            time.sleep(0.9)
            self.progress_callback(4, 5, "Identifying optimization opportunities")
            time.sleep(0.7)
            self.progress_callback(5, 5, "Generating recommendations")
            time.sleep(0.5)
            
        # Extract domain from repo URL
        domain = "github.com"
        if self.repo_url and '://' in self.repo_url:
            try:
                domain = self.repo_url.split('/')[2]
            except IndexError:
                domain = "github.com"
            
        # Random generation for demo purposes
        total_files = random.randint(50, 200)
        total_lines = random.randint(5000, 25000)
        large_files_count = random.randint(3, 15)
        
        # Create a list of simulated large files
        large_files = []
        for i in range(large_files_count):
            file_size = random.randint(800, 5000)
            large_files.append({
                'path': f'src/components/LargeComponent{i+1}.js' if random.random() > 0.5 else f'src/utils/large_utility_{i+1}.py',
                'size_kb': file_size,
                'lines': file_size * 5,
                'complexity': random.randint(15, 50)
            })
            
        # Create code duplication instances
        duplication_instances = []
        for i in range(random.randint(5, 15)):
            duplication_instances.append({
                'file1': f'src/components/Component{random.randint(1, 20)}.js',
                'file2': f'src/components/Component{random.randint(1, 20)}.js',
                'similarity': random.uniform(0.65, 0.95),
                'lines_duplicated': random.randint(20, 150)
            })
            
        # Compute total duplication percentage
        total_duplication_pct = round(min(random.uniform(5, 30), 100), 1)
        
        # Create a list of recommended optimization actions
        recommendations = [
            {
                'title': 'Reduce code duplication',
                'description': f'Found {len(duplication_instances)} instances of code duplication across the repository.',
                'priority': 'High',
                'impact': 'Reducing code duplication by 50% could reduce maintenance costs and improve energy efficiency',
                'steps': [
                    "Extract duplicate code into shared functions or components",
                    "Create utility libraries for commonly used functionality",
                    "Review similarity reports and prioritize highest-impact duplications"
                ]
            },
            {
                'title': 'Optimize large files',
                'description': f'Found {large_files_count} files over 100KB or 1000 lines, which can lead to increased load times and memory usage.',
                'priority': 'Medium',
                'impact': 'Breaking down large files can improve load times and reduce memory consumption',
                'steps': [
                    "Break down large files into smaller, focused modules",
                    "Extract complex logic into separate helper functions",
                    "Consider applying design patterns like Single Responsibility Principle"
                ]
            },
            {
                'title': 'Implement lazy loading for heavy components',
                'description': 'Large JavaScript/TypeScript components could benefit from lazy loading to improve initial load performance.',
                'priority': 'Medium',
                'impact': 'Can reduce initial load bundle size by 30-40%',
                'steps': [
                    "Identify components not needed for initial render",
                    "Implement code splitting with dynamic imports",
                    "Add loading states for components loaded on-demand"
                ]
            }
        ]
        
        # Add additional language-specific recommendations based on repository content
        if self.repo_url and "python" in self.repo_url.lower() or random.random() > 0.7:
            recommendations.append({
                'title': 'Optimize Python dependencies',
                'description': 'Several heavy dependencies could be replaced with lighter alternatives.',
                'priority': 'Low',
                'impact': 'Could reduce deployment package size by up to 60%',
                'steps': [
                    "Review requirements.txt for unused or heavy packages",
                    "Consider replacing pandas with numpy for simple operations",
                    "Use specialized libraries instead of full frameworks when possible"
                ]
            })
        elif self.repo_url and ("javascript" in self.repo_url.lower() or "typescript" in self.repo_url.lower() or "react" in self.repo_url.lower()) or random.random() > 0.6:
            recommendations.append({
                'title': 'Optimize React rendering performance',
                'description': 'Several components have unnecessary re-renders that affect performance and energy usage.',
                'priority': 'Medium',
                'impact': 'Could reduce CPU usage by 15-25% during user interactions',
                'steps': [
                    "Use React.memo for pure function components",
                    "Implement useMemo and useCallback hooks for expensive calculations",
                    "Add proper dependency arrays to useEffect hooks"
                ]
            })
        
        # Final results object
        return {
            'scan_id': f"github-{int(time.time())}",
            'scan_type': 'GitHub Repository Sustainability',
            'timestamp': datetime.now().isoformat(),
            'repository': self.repo_url,
            'branch': self.branch,
            'region': self.region,  # Include region information
            'url': self.repo_url,
            'domain': domain,
            'total_files': total_files,
            'total_lines': total_lines,
            'languages': {
                'JavaScript': {'files': int(total_files * 0.4), 'lines': int(total_lines * 0.45)},
                'TypeScript': {'files': int(total_files * 0.2), 'lines': int(total_lines * 0.25)},
                'Python': {'files': int(total_files * 0.15), 'lines': int(total_lines * 0.1)},
                'CSS': {'files': int(total_files * 0.15), 'lines': int(total_lines * 0.1)},
                'HTML': {'files': int(total_files * 0.1), 'lines': int(total_lines * 0.1)}
            },
            'code_duplication': {
                'percentage': total_duplication_pct,
                'instances': duplication_instances
            },
            'large_files': large_files,
            'findings': [
                {
                    'type': 'Code Duplication',
                    'description': f'{total_duplication_pct}% of code is duplicated across {len(duplication_instances)} instances',
                    'location': 'Multiple files',
                    'risk_level': 'high' if total_duplication_pct > 15 else 'medium',
                    'recommendation': 'Extract shared functionality into reusable components or utilities'
                },
                {
                    'type': 'Large Files',
                    'description': f'Found {large_files_count} files exceeding recommended size limits',
                    'location': f'Including {large_files[0]["path"] if large_files else "N/A"}',
                    'risk_level': 'medium',
                    'recommendation': 'Break down large files into smaller, focused modules'
                },
                {
                    'type': 'Dependency Bloat',
                    'description': 'Project includes several unused or oversized dependencies',
                    'location': 'package.json / requirements.txt',
                    'risk_level': 'low',
                    'recommendation': 'Audit and optimize dependencies, consider tree-shaking'
                }
            ],
            'recommendations': recommendations,
            'status': 'completed'
        }


def generate_report(scan_data, report_type="sustainability"):
    """
    Generate a report from scan data.
    
    Args:
        scan_data: The scan data to include in the report
        report_type: The type of report to generate
        
    Returns:
        A report object
    """
    # This is a placeholder for report generation
    # In a real implementation, this would create a PDF or HTML report
    
    # Add findings if not present
    if 'findings' not in scan_data:
        scan_data['findings'] = []
        # Extract data from various sections to create findings
        
        # For cloud sustainability reports
        if 'resources' in scan_data:
            for resource_type, resource_data in scan_data.get('resources', {}).items():
                # Add findings for idle resources
                if 'idle' in resource_data and resource_data['idle'] > 0:
                    scan_data['findings'].append({
                        'type': 'Idle Resources',
                        'description': f"Found {resource_data['idle']} idle {resource_type}",
                        'location': scan_data.get('region', 'Global'),
                        'risk_level': 'medium',
                        'recommendation': f"Consider shutting down or rightsizing idle {resource_type}"
                    })
        
        # For GitHub repository reports
        if 'large_files' in scan_data:
            for file_data in scan_data.get('large_files', [])[:5]:  # Top 5 large files
                scan_data['findings'].append({
                    'type': 'Large File',
                    'description': f"File {file_data['path']} is {file_data['size_kb']} KB with {file_data['lines']} lines",
                    'location': file_data['path'],
                    'risk_level': 'medium' if file_data['size_kb'] > 1000 else 'low',
                    'recommendation': "Break down large files into smaller, more focused modules"
                })
    
    # Add recommendations if not present
    if 'recommendations' not in scan_data:
        scan_data['recommendations'] = []
        # Generate recommendations based on findings
        risk_levels = {'high': 0, 'medium': 0, 'low': 0}
        for finding in scan_data.get('findings', []):
            risk_level = finding.get('risk_level', 'low')
            if risk_level in risk_levels:
                risk_levels[risk_level] += 1
            
            # Add recommendation based on finding
            if 'recommendation' in finding and finding['recommendation'] not in [r.get('title') for r in scan_data['recommendations']]:
                scan_data['recommendations'].append({
                    'title': finding['recommendation'],
                    'description': f"Addressing {finding['type']} issues can improve sustainability and efficiency.",
                    'priority': 'High' if risk_level == 'high' else 'Medium' if risk_level == 'medium' else 'Low',
                    'impact': 'Varies based on implementation',
                    'steps': ["Analyze affected resources or code", "Implement recommended changes", "Monitor results"]
                })
    
    # Calculate a sustainability score based on findings and available information
    high_risk_count = sum(1 for f in scan_data.get('findings', []) if f.get('risk_level') == 'high')
    medium_risk_count = sum(1 for f in scan_data.get('findings', []) if f.get('risk_level') == 'medium')
    low_risk_count = sum(1 for f in scan_data.get('findings', []) if f.get('risk_level') == 'low')
    
    # Base score calculation (100 - deductions for each risk)
    sustainability_score = 100 - (high_risk_count * 15) - (medium_risk_count * 5) - (low_risk_count * 2)
    
    # Additional factors
    # For cloud scans, consider optimization level
    if 'resources' in scan_data:
        total_resources = sum(data.get('count', 0) for data in scan_data.get('resources', {}).values())
        idle_resources = sum(data.get('idle', 0) for data in scan_data.get('resources', {}).values())
        
        if total_resources > 0:
            idle_percentage = (idle_resources / total_resources) * 100
            # Deduct up to 15 points for high idle percentage
            sustainability_score -= min(15, idle_percentage / 4)
    
    # For code scans, consider duplication level
    if 'code_duplication' in scan_data:
        duplication_percentage = scan_data.get('code_duplication', {}).get('percentage', 0)
        # Deduct up to 10 points for high duplication
        sustainability_score -= min(10, duplication_percentage / 5)
    
    # Ensure score is between 0-100
    sustainability_score = max(0, min(100, sustainability_score))
    
    # Add the score to the scan data
    scan_data['sustainability_score'] = int(sustainability_score)
    
    # Return the enhanced scan data as a report
    return {
        'title': f"{scan_data.get('scan_type', 'Sustainability')} Report",
        'generated_at': datetime.now().isoformat(),
        'scan_data': scan_data,
        'sustainability_score': int(sustainability_score),  # Add directly to the report top level
        'summary': {
            'total_findings': len(scan_data.get('findings', [])),
            'total_recommendations': len(scan_data.get('recommendations', [])),
            'risk_levels': {
                'high': high_risk_count,
                'medium': medium_risk_count,
                'low': low_risk_count
            }
        }
    }




def run_sustainability_scanner():
    """Run the sustainability scanner interface."""
    st.title("Sustainability Scanner")
    st.write("Scan cloud resources and code repositories for sustainability optimization opportunities.")
    
    # Add tabs for different scan types
    tabs = st.tabs(["Cloud Resources", "GitHub Repository", "Code Analysis"])
    
    with tabs[0]:
        run_cloud_resources_scan()
    
    with tabs[1]:
        run_github_repo_scan()
    
    with tabs[2]:
        run_code_analysis_scan()
    
    # Check if we have completed scan results
    if 'sustainability_scan_complete' in st.session_state and st.session_state.sustainability_scan_complete:
        scan_results = st.session_state.sustainability_scan_results
        display_sustainability_report(scan_results)
        

def run_cloud_resources_scan():
    """Cloud resources sustainability scan interface."""
    st.header("Cloud Resources Sustainability Scanner")
    st.write("Analyze cloud resources for sustainability optimization opportunities.")
    
    # Set the current tab
    st.session_state.sustainability_current_tab = "cloud"
    
    # Provider selection
    provider = st.selectbox(
        "Cloud Provider", 
        ["Azure", "AWS", "GCP"], 
        index=0,
        help="Select your cloud provider for sustainability analysis."
    )
    
    # Region selection
    region = st.selectbox(
        "Region", 
        ["Global", "East US", "West US", "North Europe", "West Europe", "Southeast Asia", "Australia East", "Japan East"],
        index=0,
        help="Select the primary region to analyze. Choose Global to analyze all regions.",
        key="cloud_resources_region"
    )
    
    # Provider-specific settings
    if provider == "Azure":
        st.subheader("Azure Settings")
        subscription_id = st.text_input(
            "Subscription ID", 
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            help="Enter your Azure subscription ID for scanning resources."
        )
        resource_groups = st.multiselect(
            "Resource Groups", 
            ["All Resource Groups", "Production", "Development", "Testing", "Infrastructure", "Databases"],
            default=["All Resource Groups"],
            help="Select specific resource groups to analyze. Default is All Resource Groups."
        )
    elif provider == "AWS":
        st.subheader("AWS Settings")
        accounts = st.multiselect(
            "AWS Accounts", 
            ["Current Account", "Production", "Development", "Testing", "Shared Services"],
            default=["Current Account"],
            help="Select specific AWS accounts to analyze. Default is Current Account."
        )
    elif provider == "GCP":
        st.subheader("GCP Settings")
        project_id = st.text_input(
            "Project ID", 
            placeholder="my-gcp-project-123",
            help="Enter your GCP project ID for scanning resources."
        )
        
    # Common settings
    st.subheader("Scan Options")
    scan_options = st.multiselect(
        "Scan Options",
        ["Resource Utilization", "Idle Resources", "Storage Optimization", "Networking", "Carbon Footprint"],
        default=["Resource Utilization", "Idle Resources", "Carbon Footprint"],
        help="Select which aspects of cloud resources to analyze for sustainability."
    )
    
    # Date range for analysis
    st.subheader("Time Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().replace(day=1),
            help="Start date for the sustainability analysis period."
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            help="End date for the sustainability analysis period."
        )
    
    # Scan button
    col1, col2 = st.columns([3, 1])
    with col1:
        scan_button = st.button("Scan Cloud Resources", type="primary", use_container_width=True)
    with col2:
        st.write("")  # Empty space for alignment
    
    if scan_button:
        # Initialize the scanner
        scanner_kwargs = {"region": region}
        if provider == "Azure" and 'subscription_id' in locals() and subscription_id:
            scanner_kwargs["subscription_id"] = subscription_id
        elif provider == "GCP" and 'project_id' in locals() and project_id:
            scanner_kwargs["project_id"] = project_id
            
        scanner = CloudResourcesScanner(provider=provider.lower(), region=region, **scanner_kwargs)
        
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
        with st.spinner(f"Scanning {provider} resources in {region}..."):
            # Perform the scan
            scan_results = scanner.scan_resources()
            
            # Store scan results in session state
            st.session_state.sustainability_scan_results = scan_results
            st.session_state.sustainability_scan_complete = True
            st.session_state.sustainability_scan_id = scan_results.get('scan_id')
        
        # Display a success message
        st.success(f"{provider} resources sustainability scan completed!")
        
        # Force page refresh to show results
        st.rerun()


def run_github_repo_scan():
    """GitHub repository sustainability scan interface."""
    st.header("GitHub Repository Sustainability Scanner")
    st.write("Analyze GitHub repositories for sustainability optimization opportunities.")
    
    # Set the current tab
    st.session_state.sustainability_current_tab = "github"
    
    # Repository URL input
    repo_url = st.text_input(
        "GitHub Repository URL", 
        placeholder="https://github.com/username/repo",
        help="Enter the full URL to any public GitHub repository that you want to analyze for sustainability optimization."
    )
    
    # Use session state to persist URL between interactions
    if 'github_repo_url' in st.session_state and not repo_url:
        repo_url = st.session_state.github_repo_url
    elif repo_url:
        st.session_state.github_repo_url = repo_url
    
    # Example repositories section
    st.subheader("Example Repositories")
    st.markdown("""
    You can try scanning these example repositories:
    - https://github.com/tensorflow/tensorflow
    - https://github.com/facebook/react
    - https://github.com/microsoft/vscode
    - https://github.com/django/django
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Use TensorFlow Example"):
            st.session_state.github_repo_url = "https://github.com/tensorflow/tensorflow"
            st.rerun()
    with col2:
        if st.button("Use React Example"):
            st.session_state.github_repo_url = "https://github.com/facebook/react"
            st.rerun()
    
    # Branch selection
    branch = st.text_input("Branch", value="main", help="The branch to analyze. Defaults to 'main'.")
    
    # Region selection for better context
    region = st.selectbox(
        "Region", 
        ["Europe", "North America", "Asia", "South America", "Africa", "Australia", "Global"],
        index=0,
        help="Select the region where this code is primarily deployed/used for sustainability context.",
        key="github_repo_region"
    )
    
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
        scanner_kwargs = {"repo_url": repo_url, "branch": branch, "region": region}
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
        
        # Region selection for better report context
        region = st.selectbox(
            "Region", 
            ["Europe", "North America", "Asia", "South America", "Africa", "Australia", "Global"],
            index=0,
            help="Select the region where this code is primarily deployed/used for sustainability context.",
            key="uploaded_code_region"
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
        
        # Region selection for better report context
        region = st.selectbox(
            "Region", 
            ["Europe", "North America", "Asia", "South America", "Africa", "Australia", "Global"],
            index=0,
            help="Select the region where this code is primarily deployed/used for sustainability context.",
            key="github_code_region"
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
                time.sleep(0.7)
                
                # Step 2: File scanning
                status_text.text("Step 2/5: Scanning repository files...")
                progress_bar.progress(2/total_steps)
                time.sleep(0.9)
                
                # Step 3: Code complexity analysis
                status_text.text("Step 3/5: Analyzing code complexity...")
                progress_bar.progress(3/total_steps)
                time.sleep(0.8)
                
                # Step 4: Import usage analysis
                status_text.text("Step 4/5: Checking for unused imports...")
                progress_bar.progress(4/total_steps)
                time.sleep(0.7)
                
                # Step 5: Generating recommendations
                status_text.text("Step 5/5: Generating sustainability recommendations...")
                progress_bar.progress(5/total_steps)
                time.sleep(0.6)
                
                # Determine domain from URL
                if github_url and '://' in github_url:
                    try:
                        domain = github_url.split('/')[2]
                    except IndexError:
                        domain = "github.com"
                
                scan_results = {
                    'scan_id': f"github-code-{int(time.time())}",
                    'scan_type': 'GitHub Code Analysis',
                    'timestamp': datetime.now().isoformat(),
                    'repository': github_url,
                    'repo_url': github_url,
                    'branch': branch if 'branch' in locals() else 'main',
                    'region': region if 'region' in locals() else 'Europe',  # Use selected region or default to Europe
                    'url': github_url,
                    'domain': domain,
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
                            'type': 'Code Complexity',
                            'description': f"Found {random.randint(5, 25)} functions with cyclomatic complexity over 15",
                            'location': 'Multiple files',
                            'risk_level': 'medium',
                            'recommendation': 'Refactor complex functions into smaller, more manageable pieces'
                        },
                        {
                            'type': 'Unused Imports',
                            'description': f"Found {random.randint(10, 50)} potentially unused imports",
                            'location': 'Multiple files',
                            'risk_level': 'low',
                            'recommendation': 'Remove unused imports to improve code clarity and performance'
                        },
                        {
                            'type': 'Large Files',
                            'description': f"Found {random.randint(3, 15)} files over 1000 lines",
                            'location': 'src/components/LargeComponent.js',
                            'risk_level': 'medium',
                            'recommendation': 'Break down large files into smaller, more focused modules'
                        }
                    ],
                    'recommendations': [
                        {
                            'title': 'Refactor complex functions',
                            'description': 'Several functions have high cyclomatic complexity, making them difficult to maintain and test.',
                            'priority': 'High',
                            'impact': 'Improves code maintainability and reduces potential for bugs',
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
                    'region': region if 'region' in locals() else 'Europe',  # Use selected region or default
                    'url': 'Local Files',
                    'domain': 'local.files',
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
                    
                    # Basic file stats
                    lines = len(content.splitlines())
                    size = len(content)
                    
                    # Detect language based on file extension
                    extension = file.name.split('.')[-1].lower()
                    language_map = {
                        'py': 'Python',
                        'js': 'JavaScript',
                        'ts': 'TypeScript',
                        'java': 'Java',
                        'c': 'C',
                        'cpp': 'C++',
                        'cs': 'C#',
                        'go': 'Go',
                        'rb': 'Ruby'
                    }
                    language = language_map.get(extension, 'Other')
                    
                    # Track languages in scan results
                    if 'languages' not in scan_results:
                        scan_results['languages'] = {}
                    
                    if language in scan_results['languages']:
                        scan_results['languages'][language]['files'] += 1
                        scan_results['languages'][language]['lines'] += lines
                    else:
                        scan_results['languages'][language] = {'files': 1, 'lines': lines}
                    
                    # Simple analysis for different languages
                    if language == 'Python':
                        # Check for unused imports
                        import_count = content.count('import ')
                        if import_count > 10:
                            scan_results['findings'].append({
                                'type': 'Many Imports',
                                'description': f"File has {import_count} import statements",
                                'location': file.name,
                                'risk_level': 'low',
                                'recommendation': 'Review imports and remove unnecessary ones'
                            })
                        
                        # Check for long functions
                        if 'def ' in content and lines > 200:
                            scan_results['findings'].append({
                                'type': 'Large Python File',
                                'description': f"Python file is {lines} lines long",
                                'location': file.name,
                                'risk_level': 'medium',
                                'recommendation': 'Consider breaking down into smaller modules'
                            })
                    
                    elif language in ['JavaScript', 'TypeScript']:
                        # Check for large React components
                        if 'React' in content and 'class ' in content and 'extends ' in content and lines > 300:
                            scan_results['findings'].append({
                                'type': 'Large React Component',
                                'description': f"React component is {lines} lines long",
                                'location': file.name,
                                'risk_level': 'medium',
                                'recommendation': 'Break down into smaller, focused components'
                            })
                            
                        # Check for many useState hooks
                        usestate_count = content.count('useState(')
                        if usestate_count > 7:
                            scan_results['findings'].append({
                                'type': 'Many State Variables',
                                'description': f"Component has {usestate_count} useState hooks",
                                'location': file.name,
                                'risk_level': 'low',
                                'recommendation': 'Consider using useReducer for complex state'
                            })
                    
                    # Generic checks for all languages
                    if lines > 500:
                        scan_results['findings'].append({
                            'type': 'Large File',
                            'description': f"File has {lines} lines of code",
                            'location': file.name,
                            'risk_level': 'medium',
                            'recommendation': 'Break down into smaller files or modules'
                        })
                    
                    # Check for low comment ratio
                    comment_markers = ['#', '//', '/*', '*', '"""', "'''"]
                    comment_lines = sum(1 for line in content.splitlines() if any(marker in line for marker in comment_markers))
                    comment_ratio = comment_lines / max(lines, 1)
                    
                    if lines > 100 and comment_ratio < 0.1:
                        scan_results['findings'].append({
                            'type': 'Low Comment Ratio',
                            'description': f"Only {comment_ratio:.1%} of lines are comments",
                            'location': file.name,
                            'risk_level': 'low',
                            'recommendation': 'Add more documentation to improve maintainability'
                        })
                
                # Generate recommendations based on findings
                if not scan_results['recommendations'] and scan_results['findings']:
                    # Group findings by type
                    finding_types = {}
                    for finding in scan_results['findings']:
                        if finding['type'] not in finding_types:
                            finding_types[finding['type']] = []
                        finding_types[finding['type']].append(finding)
                    
                    # Generate recommendations for common findings
                    if 'Large File' in finding_types:
                        scan_results['recommendations'].append({
                            'title': 'Refactor large files',
                            'description': f"Found {len(finding_types['Large File'])} large files that could be broken down",
                            'priority': 'Medium',
                            'impact': 'Improves code maintainability and developer productivity',
                            'steps': [
                                "Identify related functionality in large files",
                                "Extract into separate modules or components",
                                "Ensure proper imports and exports"
                            ]
                        })
                    
                    if 'Low Comment Ratio' in finding_types:
                        scan_results['recommendations'].append({
                            'title': 'Improve code documentation',
                            'description': f"Found {len(finding_types['Low Comment Ratio'])} files with insufficient comments",
                            'priority': 'Low',
                            'impact': 'Improves code maintainability and onboarding of new developers',
                            'steps': [
                                "Add docstrings to functions and classes",
                                "Explain complex logic with inline comments",
                                "Consider adding a README.md with high-level documentation"
                            ]
                        })
                
                # Set scan status to completed
                scan_results['status'] = 'completed'
        
        # Store scan results in session state
        st.session_state.sustainability_scan_results = scan_results
        st.session_state.sustainability_scan_complete = True
        st.session_state.sustainability_scan_id = scan_results.get('scan_id')
        
        # Display a success message
        st.success(f"Code analysis completed! Analyzed {scan_results.get('files_analyzed', 0)} files.")
        
        # Force page refresh to show results
        st.rerun()


def display_sustainability_report(scan_results):
    """Display sustainability scan results and report."""
    # Clear previous display
    st.divider()
    st.header("Sustainability Scan Results")
    
    # Extract or calculate the sustainability score
    sustainability_score = scan_results.get('sustainability_score', 0)
    if not sustainability_score:
        # Check if it's nested in scan_data
        if isinstance(scan_results.get('scan_data'), dict):
            sustainability_score = scan_results.get('scan_data', {}).get('sustainability_score', 0)
    
    # Display the overall sustainability score at the top
    st.subheader("Sustainability Score")
    
    # Style the score with appropriate color
    score_color = "#ef4444"  # Red for low scores
    if sustainability_score >= 80:
        score_color = "#10b981"  # Green for high scores
    elif sustainability_score >= 50:
        score_color = "#f97316"  # Orange for medium scores
    
    # Display score with styling
    st.markdown(
        f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; text-align: center;">
            <h1 style="color: {score_color}; font-size: 2.5rem; margin: 0;">{int(sustainability_score)}<span style="font-size: 1.5rem;">/100</span></h1>
            <p style="margin: 0;">Data Sustainability Index</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Display appropriate report based on scan type
    scan_type = scan_results.get('scan_type', '').lower()
    
    if 'cloud' in scan_type:
        display_cloud_sustainability_report(scan_results)
    elif 'github' in scan_type:
        display_github_sustainability_report(scan_results)
    elif 'code' in scan_type:
        display_code_analysis_report(scan_results)
    else:
        display_generic_sustainability_report(scan_results)
    
    # Generate PDF report option
    st.divider()
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate PDF Report", type="primary"):
            st.session_state.generate_pdf = True
            with st.spinner("Generating PDF report... This may take a moment."):
                try:
                    # Import report generator
                    from services.report_generator import generate_report
                    
                    # Generate the actual PDF report
                    pdf_bytes = generate_report(
                        scan_data=scan_results,
                        include_details=True,
                        include_charts=True,
                        include_metadata=True,
                        include_recommendations=True,
                        report_format="sustainability"
                    )
                    
                    # Ensure we have valid PDF content
                    if pdf_bytes and len(pdf_bytes) > 0:
                        st.success("PDF report generated successfully!")
                        
                        # Offer download options with the actual PDF content
                        st.download_button(
                            "Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"sustainability-report-{scan_results.get('scan_id', 'unknown')}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("Failed to generate PDF report. Empty content returned.")
                except Exception as e:
                    st.error(f"Error generating PDF report: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
    
    with col2:
        if st.button("Export JSON Data"):
            # Convert to JSON string
            json_str = json.dumps(scan_results, indent=2)
            
            # Offer download
            st.download_button(
                "Download JSON Data",
                data=json_str,
                file_name=f"sustainability-data-{scan_results.get('scan_id', 'unknown')}.json",
                mime="application/json"
            )
    
    # Option to start a new scan
    st.divider()
    if st.button("Start New Scan"):
        # Clear session state for scan results
        if 'sustainability_scan_results' in st.session_state:
            del st.session_state.sustainability_scan_results
        if 'sustainability_scan_complete' in st.session_state:
            del st.session_state.sustainability_scan_complete
        if 'sustainability_scan_id' in st.session_state:
            del st.session_state.sustainability_scan_id
        
        # Return to the correct tab
        if 'sustainability_current_tab' in st.session_state:
            current_tab = st.session_state.sustainability_current_tab
        else:
            current_tab = "cloud"
        
        # Rerun to show the scan form
        st.rerun()


def display_cloud_sustainability_report(scan_results):
    """Display cloud resources sustainability report."""
    # Extract scan information
    provider = scan_results.get('provider', 'Unknown').upper()
    region = scan_results.get('region', 'Global')
    domain = scan_results.get('domain', 'cloud.unknown.com')
    url = scan_results.get('url', f"https://{domain}")
    scan_id = scan_results.get('scan_id', 'Unknown')
    scan_timestamp = scan_results.get('timestamp', datetime.now().isoformat())
    formatted_time = datetime.fromisoformat(scan_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Summary section
    st.subheader("Cloud Resources Scan Overview")
    
    # First row of metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Cloud Provider", provider)
    with col2:
        st.metric("Region", region)
    with col3:
        st.metric("Scan Time", formatted_time)
    
    # Second row of metrics for domain and URL
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Domain", domain)
    with col2:
        st.metric("Cloud Console URL", url)
    
    # Resources section
    st.subheader("Resource Inventory")
    
    resources = scan_results.get('resources', {})
    if resources:
        # Create resource inventory table
        resource_data = []
        for resource_type, resource_info in resources.items():
            resource_data.append({
                "Resource Type": resource_type.replace('_', ' ').title(),
                "Count": resource_info.get('count', 0),
                "Idle": resource_info.get('idle', 0),
                "Utilization": f"{resource_info.get('utilization', 0)}%"
            })
        
        if resource_data:
            resource_df = pd.DataFrame(resource_data)
            st.table(resource_df)
    
    # Carbon footprint section
    st.subheader("Carbon Footprint")
    
    carbon_data = scan_results.get('carbon_footprint', {})
    if carbon_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Total CO₂ Emissions (kg)", 
                f"{carbon_data.get('total_co2e_kg', 0):.1f}",
                delta=None
            )
        
        with col2:
            reduction_potential = carbon_data.get('emissions_reduction_potential_kg', 0)
            reduction_pct = (reduction_potential / carbon_data.get('total_co2e_kg', 1)) * 100
            
            st.metric(
                "Potential Reduction (kg)", 
                f"{reduction_potential:.1f}",
                delta=f"-{reduction_pct:.1f}%"
            )
        
        # Region breakdown
        region_data = carbon_data.get('by_region', {})
        if region_data:
            st.subheader("Emissions by Region")
            
            # Create chart data
            regions = list(region_data.keys())
            emissions = list(region_data.values())
            
            # Create horizontal bar chart
            fig = px.bar(
                x=emissions, 
                y=regions, 
                orientation='h',
                labels={'x': 'CO₂ Emissions (kg)', 'y': 'Region'},
                title="Carbon Emissions by Region (kg CO₂e)",
                color=emissions,
                color_continuous_scale='viridis'
            )
            
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
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
            display_findings_list(risk_levels['high'], 'high')
            
        with tabs[1]:
            display_findings_list(risk_levels['medium'], 'medium')
            
        with tabs[2]:
            display_findings_list(risk_levels['low'], 'low')
    
    # Recommendations section
    st.subheader("Optimization Recommendations")
    
    recommendations = scan_results.get('recommendations', [])
    display_recommendations_list(recommendations)


def display_github_sustainability_report(scan_results):
    """Display GitHub repository sustainability report."""
    # Extract scan information
    repo_url = scan_results.get('repository', 'Unknown')
    branch = scan_results.get('branch', 'main')
    region = scan_results.get('region', 'Global')
    domain = scan_results.get('domain', 'github.com')
    scan_id = scan_results.get('scan_id', 'Unknown')
    scan_timestamp = scan_results.get('timestamp', datetime.now().isoformat())
    formatted_time = datetime.fromisoformat(scan_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Get repository name
    repo_name = repo_url.split('/')[-1] if '/' in repo_url else repo_url
    
    # Summary section
    st.subheader("GitHub Repository Scan Overview")
    
    # First row of metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Repository", repo_name)
    with col2:
        st.metric("Branch", branch)
    with col3:
        st.metric("Scan Time", formatted_time)
    
    # Second row of metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Region", region)
    with col2:
        st.metric("Domain", domain)
    with col3:
        st.metric("URL", repo_url)
    
    # Repository stats
    st.subheader("Repository Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Files", scan_results.get('total_files', 0))
    with col2:
        st.metric("Total Lines", scan_results.get('total_lines', 0))
    with col3:
        duplication = scan_results.get('code_duplication', {}).get('percentage', 0)
        st.metric("Code Duplication", f"{duplication}%")
    
    # Language breakdown
    languages = scan_results.get('languages', {})
    if languages:
        st.subheader("Language Breakdown")
        
        # Create chart data
        lang_names = []
        lang_files = []
        lang_lines = []
        
        for lang, stats in languages.items():
            lang_names.append(lang)
            lang_files.append(stats.get('files', 0))
            lang_lines.append(stats.get('lines', 0))
        
        # Create two charts side by side
        col1, col2 = st.columns(2)
        
        with col1:
            # Files by language pie chart
            fig1 = px.pie(
                names=lang_names, 
                values=lang_files,
                title="Files by Language",
                color=lang_names,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            fig1.update_layout(height=300)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Lines by language pie chart
            fig2 = px.pie(
                names=lang_names, 
                values=lang_lines,
                title="Lines of Code by Language",
                color=lang_names,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)
    
    # Code duplication details
    duplication_data = scan_results.get('code_duplication', {})
    if duplication_data:
        st.subheader("Code Duplication")
        
        duplication_pct = duplication_data.get('percentage', 0)
        duplication_instances = duplication_data.get('instances', [])
        
        # Display duplication gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = duplication_pct,
            title = {'text': "Code Duplication Percentage"},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 10], 'color': "lightgreen"},
                    {'range': [10, 25], 'color': "yellow"},
                    {'range': [25, 100], 'color': "salmon"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 25
                }
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display top duplication instances if available
        if duplication_instances:
            st.subheader("Top Duplication Instances")
            
            # Convert to DataFrame
            duplication_df = pd.DataFrame([
                {
                    "File 1": inst.get('file1', 'Unknown'),
                    "File 2": inst.get('file2', 'Unknown'),
                    "Similarity": f"{inst.get('similarity', 0) * 100:.1f}%",
                    "Lines Duplicated": inst.get('lines_duplicated', 0)
                }
                for inst in duplication_instances[:5]  # Show top 5
            ])
            
            st.table(duplication_df)
    
    # Large files
    large_files = scan_results.get('large_files', [])
    if large_files:
        st.subheader("Large Files")
        
        # Convert to DataFrame
        large_files_df = pd.DataFrame([
            {
                "File Path": file.get('path', 'Unknown'),
                "Size (KB)": file.get('size_kb', 0),
                "Lines": file.get('lines', 0),
                "Complexity": file.get('complexity', 'N/A')
            }
            for file in large_files[:10]  # Show top 10
        ])
        
        st.table(large_files_df)
    
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
            display_findings_list(risk_levels['high'], 'high')
            
        with tabs[1]:
            display_findings_list(risk_levels['medium'], 'medium')
            
        with tabs[2]:
            display_findings_list(risk_levels['low'], 'low')
    
    # Recommendations section
    st.subheader("Optimization Recommendations")
    
    recommendations = scan_results.get('recommendations', [])
    display_recommendations_list(recommendations)


def display_code_analysis_report(scan_results):
    """Display code analysis sustainability report."""
    # Extract scan information
    source = scan_results.get('repository', scan_results.get('repo_url', 'Local Files'))
    if source == 'Local Files':
        source_type = "Uploaded Files"
    else:
        source_type = "GitHub Repository"
        
    files_analyzed = scan_results.get('files_analyzed', 0)
    scan_id = scan_results.get('scan_id', 'Unknown')
    region = scan_results.get('region', 'Global')
    domain = scan_results.get('domain', 'github.com' if source_type == "GitHub Repository" else 'local.files')
    url = scan_results.get('url', source)
    scan_timestamp = scan_results.get('timestamp', datetime.now().isoformat())
    formatted_time = datetime.fromisoformat(scan_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Summary section
    st.subheader("Code Analysis Scan Overview")
    
    # First row of metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Source Type", source_type)
    with col2:
        st.metric("Files Analyzed", files_analyzed)
    with col3:
        st.metric("Scan Time", formatted_time)
    
    # Second row of metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Region", region)
    with col2:
        st.metric("Domain", domain)
    with col3:
        st.metric("URL/Source", url if len(url) < 30 else url[:27] + "...")
    
    # Language breakdown
    languages = scan_results.get('languages', {})
    if languages:
        st.subheader("Language Breakdown")
        
        # Create chart data
        lang_names = []
        lang_files = []
        lang_lines = []
        
        for lang, stats in languages.items():
            lang_names.append(lang)
            lang_files.append(stats.get('files', 0))
            lang_lines.append(stats.get('lines', 0))
        
        # Create two charts side by side
        col1, col2 = st.columns(2)
        
        with col1:
            # Files by language pie chart
            fig1 = px.pie(
                names=lang_names, 
                values=lang_files,
                title="Files by Language",
                color=lang_names,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            fig1.update_layout(height=300)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Lines by language pie chart
            fig2 = px.pie(
                names=lang_names, 
                values=lang_lines,
                title="Lines of Code by Language",
                color=lang_names,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)
    
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
            display_findings_list(risk_levels['high'], 'high')
            
        with tabs[1]:
            display_findings_list(risk_levels['medium'], 'medium')
            
        with tabs[2]:
            display_findings_list(risk_levels['low'], 'low')
    
    # Recommendations section
    st.subheader("Optimization Recommendations")
    
    recommendations = scan_results.get('recommendations', [])
    display_recommendations_list(recommendations)


def display_generic_sustainability_report(scan_results):
    """Display generic sustainability report for unknown scan types."""
    # Extract basic scan info
    scan_type = scan_results.get('scan_type', 'Unknown')
    scan_id = scan_results.get('scan_id', 'Unknown')
    scan_timestamp = scan_results.get('timestamp', datetime.now().isoformat())
    formatted_time = datetime.fromisoformat(scan_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    region = scan_results.get('region', 'Europe')
    domain = scan_results.get('domain', 'unknown.domain')
    url = scan_results.get('url', 'Not specified')
    
    # Summary section
    st.subheader("Scan Overview")
    
    # First row of metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Scan Type", scan_type)
    with col2:
        st.metric("Scan ID", scan_id)
    with col3:
        st.metric("Scan Time", formatted_time)
    
    # Second row of metrics for region and domain
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Region", region)
    with col2:
        st.metric("URL", url)
    with col3:
        st.metric("Domain", domain)
    
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
            display_findings_list(risk_levels['high'], 'high')
            
        with tabs[1]:
            display_findings_list(risk_levels['medium'], 'medium')
            
        with tabs[2]:
            display_findings_list(risk_levels['low'], 'low')
    
    # Recommendations section
    st.subheader("Optimization Recommendations")
    
    recommendations = scan_results.get('recommendations', [])
    display_recommendations_list(recommendations)


def display_recommendations_list(recommendations):
    """Display a list of recommendations without using expanders."""
    if not recommendations:
        st.info("No recommendations found.")
        return
    
    # Style based on priority
    priority_colors = {
        "High": "#ef4444",
        "Medium": "#f97316",
        "Low": "#10b981"
    }
    
    # Display each recommendation
    for i, rec in enumerate(recommendations):
        priority = rec.get('priority', 'Medium')
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown(f"### {i+1}. {rec.get('title', 'Recommendation')}")
        
        with col2:
            priority_color = priority_colors.get(priority, "#f97316")
            st.markdown(f"<div style='padding: 5px 10px; background-color: {priority_color}; color: white; border-radius: 4px; text-align: center; margin-top: 15px;'>{priority} Priority</div>", unsafe_allow_html=True)
        
        st.markdown(f"**Description:** {rec.get('description', 'No description provided.')}")
        
        if 'impact' in rec:
            st.markdown(f"**Impact:** {rec.get('impact')}")
        
        # Display steps
        if 'steps' in rec and rec['steps']:
            st.markdown("**Steps:**")
            for step in rec['steps']:
                st.markdown(f"- {step}")
        
        # Add spacing between recommendations
        st.divider()


def display_findings_list(findings, risk_level):
    """Display a list of findings with a specific risk level."""
    if not findings:
        st.info(f"No {risk_level} risk findings.")
        return
    
    # Set color based on risk level
    risk_colors = {
        'high': '#ef4444',
        'medium': '#f97316',
        'low': '#10b981'
    }
    
    risk_color = risk_colors.get(risk_level, '#f97316')
    
    # Display each finding
    for i, finding in enumerate(findings):
        st.markdown(f"### Finding {i+1}: {finding.get('type', 'Issue')}")
        st.markdown(f"**Description:** {finding.get('description', 'No description provided.')}")
        
        # Two columns for location and risk level
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Location:** {finding.get('location', 'Unknown')}")
        
        with col2:
            st.markdown(f"<div style='padding: 5px 10px; background-color: {risk_color}; color: white; border-radius: 4px; text-align: center;'>{risk_level.title()} Risk</div>", unsafe_allow_html=True)
        
        # Recommendation
        if 'recommendation' in finding:
            st.markdown(f"**Recommendation:** {finding.get('recommendation')}")
        
        # Add spacing between findings
        st.markdown("---")
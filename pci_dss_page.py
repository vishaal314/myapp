"""
PCI DSS Compliance Scanner Page

A dedicated standalone page for the PCI DSS compliance scanner
to help diagnose and fix the repository URL input field visibility issue.
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Page config
st.set_page_config(page_title="PCI DSS Scanner", layout="wide")

# Mock regions
REGIONS = {
    "Netherlands": {"lang": "nl", "flag": "🇳🇱"},
    "Germany": {"lang": "de", "flag": "🇩🇪"},
    "France": {"lang": "fr", "flag": "🇫🇷"},
    "Belgium": {"lang": "be", "flag": "🇧🇪"}
}

# Title and description
st.title("PCI DSS Compliance Scanner")
st.write(
    "Scan your codebase for Payment Card Industry Data Security Standard (PCI DSS) compliance issues. "
    "This scanner identifies security vulnerabilities, exposures, and configuration issues that could "
    "impact your ability to securely process, store, or transmit credit card data."
)

# Add more detailed info 
st.info(
    "PCI DSS scanning analyzes your code against the 12 PCI DSS requirements to identify "
    "potential compliance issues. The scanner detects insecure coding patterns, vulnerable "
    "dependencies, and configurations that could put cardholder data at risk."
)

# Show trial status notice
st.markdown("""
<div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 20px;">
    <span style="font-weight: bold;">Free Trial:</span> 3 days left
</div>
""", unsafe_allow_html=True)

# Create two columns for better UI organization
left_col, right_col = st.columns([1, 1.5])

# Left column for configuration
with left_col:
    # 1. Region Selection
    st.subheader("1. Region Selection")
    region_options = ["Global", "Netherlands", "Germany", "France", "Belgium"]
    selected_region = st.selectbox(
        "Select Region:",
        region_options,
        index=0,
        key="pcidss_region_fixed"
    )
    
    # 2. Source Configuration
    st.subheader("2. Source Configuration")
    source_type = st.radio(
        "Select Source Type:",
        ["Repository URL", "Upload Files"],
        key="pcidss_source_type_fixed"
    )
    
    # Repository Details
    if source_type == "Repository URL":
        # Repository provider selection
        repo_provider = st.radio(
            "Repository Provider:",
            ["GitHub", "BitBucket", "Azure DevOps"],
            horizontal=True,
            key="pcidss_repo_provider_fixed"
        )
        
        # Repository URL input field
        st.markdown("**Repository URL:** (Required)")
        repo_url = st.text_input(
            "Enter the repository URL",
            placeholder=f"Example: https://{repo_provider.lower()}.com/username/repo",
            key="pcidss_repo_url_fixed"
        )
        
        # Branch field
        st.markdown("**Branch:**")
        branch = st.text_input(
            "Branch name",
            value="main",
            key="pcidss_branch_fixed"
        )
    else:
        # File upload
        uploaded_files = st.file_uploader(
            "Upload code files to scan:",
            accept_multiple_files=True,
            key="pcidss_files_fixed"
        )
        
        if uploaded_files:
            st.success(f"Uploaded {len(uploaded_files)} files")
    
    # 3. Scan Options
    st.subheader("3. Scan Options")
    
    # Create columns for options
    opt_col1, opt_col2 = st.columns(2)
    
    with opt_col1:
        scan_dependencies = st.checkbox(
            "Scan Dependencies",
            value=True,
            key="pcidss_deps_fixed"
        )
        scan_iac = st.checkbox(
            "Scan Infrastructure",
            value=True,
            key="pcidss_iac_fixed"
        )
    
    with opt_col2:
        scan_secrets = st.checkbox(
            "Detect Secrets",
            value=True,
            key="pcidss_secrets_fixed"
        )
    
    # 4. Start Scan
    st.subheader("4. Start Scan")
    scan_button = st.button(
        "Start PCI DSS Scan",
        type="primary", 
        use_container_width=True,
        key="pcidss_scan_button_fixed"
    )

# Right column for results
with right_col:
    st.subheader("Scan Results")
    
    # Process scan button click
    if scan_button:
        # Validate inputs
        valid_input = True
        if source_type == "Repository URL" and not repo_url:
            st.error("Please enter a repository URL")
            valid_input = False
        elif source_type == "Upload Files" and not uploaded_files:
            st.error("Please upload at least one file")
            valid_input = False
        
        if valid_input:
            # Show scan progress
            scan_progress = st.progress(0)
            scan_status = st.empty()
            scan_status.text("Initializing scan...")
            
            # Simulate scanning process
            for i in range(10):
                # Update progress
                scan_progress.progress((i + 1) / 10)
                scan_status.text(f"Processing step {i+1}/10...")
                time.sleep(0.3)
            
            # Complete scan
            scan_progress.progress(1.0)
            scan_status.success("Scan completed successfully!")
            
            # Display mock results
            st.subheader("PCI DSS Compliance Results")
            
            # Source information
            if source_type == "Repository URL":
                st.write(f"**Repository:** {repo_url}")
                st.write(f"**Branch:** {branch}")
            else:
                st.write("**Source:** Uploaded Files")
            
            st.write(f"**Region:** {selected_region}")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Compliance Score", "78%")
            
            with col2:
                st.metric("High Risk", "3")
            
            with col3:
                st.metric("Medium Risk", "7")
            
            with col4:
                st.metric("Low Risk", "12")
            
            # Findings table
            st.subheader("Findings")
            
            # Create sample findings data
            findings = [
                {"Type": "Insecure Data Storage", "Location": "app/payments.py:45", "Risk Level": "High", "PCI Requirement": "3.4", "Description": "Credit card number stored in plaintext"},
                {"Type": "Weak Cryptography", "Location": "utils/crypto.py:28", "Risk Level": "Medium", "PCI Requirement": "4.1", "Description": "Using outdated encryption (MD5)"},
                {"Type": "Missing Authentication", "Location": "api/endpoints.py:12", "Risk Level": "High", "PCI Requirement": "8.3", "Description": "Endpoint missing multi-factor authentication"},
                {"Type": "Default Credentials", "Location": "config/database.yml", "Risk Level": "High", "PCI Requirement": "2.1", "Description": "Default database credentials in config"},
                {"Type": "Insecure Transmission", "Location": "js/checkout.js:52", "Risk Level": "Medium", "PCI Requirement": "4.1", "Description": "Payment data transmitted over HTTP"}
            ]
            
            # Convert to DataFrame
            findings_df = pd.DataFrame(findings)
            
            # Define risk highlighting function
            def highlight_risk(val):
                if val == "High":
                    return 'background-color: #FFCCCC'
                elif val == "Medium":
                    return 'background-color: #FFFFCC'
                elif val == "Low":
                    return 'background-color: #CCFFCC'
                return ''
            
            # Display styled dataframe
            st.dataframe(findings_df.style.applymap(highlight_risk, subset=['Risk Level']), use_container_width=True)
            
            # Mock recommendations
            st.subheader("Recommendations")
            recommendations = [
                "Encrypt all stored cardholder data using strong cryptography (AES-256 or better)",
                "Implement secure transmission by using TLS 1.2 or higher for all payment data",
                "Replace default credentials with strong, unique passwords",
                "Implement multi-factor authentication for all payment processing endpoints",
                "Update encryption algorithms to modern standards (avoid MD5, SHA-1)"
            ]
            
            for i, rec in enumerate(recommendations):
                st.markdown(f"**{i+1}.** {rec}")
    else:
        # Instructions
        st.info(
            "Configure scan options on the left and click 'Start PCI DSS Scan' to begin. "
            "Results will appear here after scanning is complete."
        )